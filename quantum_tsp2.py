#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Olivia Pitcl
Phys 305 Creative Project, K Johns

Implemenatation of the Travelling Salesman Problem using
the Qiskit SDK and its simulations of a quantum circuit

Sources: 
   https://qiskit.org/textbook/ch-paper-implementations/tsp.html
   https://qiskit.org/textbook/ch-algorithms/grover.html
"""

from qiskit import QuantumCircuit, Aer, QuantumRegister, ClassicalRegister, execute
from qiskit.visualization import plot_histogram, array_to_latex
from qiskit.circuit.library import QFT
from numpy import pi
import numpy as np
import matplotlib.pyplot as plt

'''
Produces the controlled unitary matrix which produces the various
Hamiltonian cycles for the Travelling Salesman problem.
From Qiskit Textbook
'''
# x,y,z = Specific Qubit; a,b,c,d = Phases
def controlled_unitary(qc, qubits: list, phases: list): 
    qc.cp(phases[2]-phases[0], qubits[0], qubits[1]) # controlled-U1(c-a)
    qc.p(phases[0], qubits[0]) # U1(a)
    qc.cp(phases[1]-phases[0], qubits[0], qubits[2]) # controlled-U1(b-a)
    
    # controlled controlled U1(d-c+a-b)
    qc.cp((phases[3]-phases[2]+phases[0]-phases[1])/2, qubits[1], qubits[2])
    qc.cx(qubits[0], qubits[1])
    qc.cp(-(phases[3]-phases[2]+phases[0]-phases[1])/2, qubits[1], qubits[2])
    qc.cx(qubits[0], qubits[1])
    qc.cp((phases[3]-phases[2]+phases[0]-phases[1])/2, qubits[0], qubits[2])


'''
Outer Product of vrious unitary matrices U1, U2,
U3, and U4
Together in a tensor product, the produce a matrix of n^n components, of
which only n-1 are Hamiltonian cycles
From Qiskit Textbook
'''
def U(times, qc, unit, eigen, phases: list): 
    # a,b,c = phases for U1; d,e,f = phases for U2; g,h,i = phases for U3; j,k,l = phases for U4; m_list=[m, n, o, p, q, r, s, t, u, a, b, c, d, e, f, g, h, i, j, k, l]
    controlled_unitary(qc, [unit[0]]+eigen[0:2], [0]+phases[0:3])
    controlled_unitary(qc, [unit[0]]+eigen[2:4], [phases[3]]+[0]+phases[4:6])
    controlled_unitary(qc, [unit[0]]+eigen[4:6], phases[6:8]+[0]+[phases[8]])
    controlled_unitary(qc, [unit[0]]+eigen[6:8], phases[9:12]+[0])
    

'''
Uses the two functions above to make the end, controlled unitary matrix

From Qiskit Textbook
'''
def final_U(times, eigen, phases: list):
    unit = QuantumRegister(1, 'unit')
    qc = QuantumCircuit(unit, eigen)
    for _ in range(2**times):
        U(times, qc, unit, eigen, phases)
    return qc.to_gate(label='U'+'_'+(str(2**times)))


# Storing the eigenstates in a list
# Each represents the path taken between 4 nodes as such:
# 11000110 can be broken up as 11 00 01 10
# This encodes 3 0 1 2, which is the result of some node n - 1
# where each combination encodes the cost of the path from n to 1
#
# Thus, the state 11 encodes the path cost from 1 to 4
eigen_values = ["11000110", "10001101", "11001001"]

# Function to place appropriate corresponding gate according to eigenstates
# Function from Qiskit Textbook
def eigenstates(qc, eigen, index):
    for i in range(0, len(eigen)):
        if eigen_values[index][i] == '1':
            qc.x(eigen[i])
        if eigen_values[index][i] == '0':
            pass
    qc.barrier()
    return qc

# Initialization
unit = QuantumRegister(6, 'unit')
eigen = QuantumRegister(8, 'eigen')
unit_classical = ClassicalRegister(6, 'unit_classical')

# ------- Read in phases ----------
# Phases are the costs of each path encoded as a ratio of 2*pi
# These costs below are in simple_graph.txt. Each cost < 10
file = open("simple_graph.txt", "r")
file.readline()
lines = file.readlines()
phases = [] # a, b, c, d, e, f, g, h, i, j, k, l
for line in lines:
    line = line.strip().split()
    for elem in line[1:]:
        # Normalize the path distances between 0 and 2pi
        if elem.isnumeric():
            num = float(elem) / 10
            if not num == 0.0:
                phases.append(num * 2 * pi)
# length must be 12 (n * (n - 1))                
print(len(phases))
file.close()

# --------- Run circuits --------------
# Setting one eigenstate  per circuit in circuits
# Playing with the first eigenstate here i.e. 11000110 from eigen_values list.
# (Try to play with other eigenstates from the eigen_values list)
circuits = []

# Track all possible outcomes in this list of dictionaries, one entry for each
# circuit run
results = []
for i in range(len(eigen_values)):
    qc = QuantumCircuit(unit, eigen, unit_classical)
    circuits.append(eigenstates(qc, eigen, i))
    #
    
    # Hadamard on the 'unit' qubits
    qc.h(unit[:])
    qc.barrier()

    for i in range(0, 6):
        qc.append(final_U(i, eigen, phases), [unit[5-i]] + eigen[:])
    #
    
    # Inverse QFT 
    qc.barrier()
    qft = QFT(num_qubits=len(unit), inverse=True, insert_barriers=True, do_swaps=False, name='Inverse QFT')
    qc.append(qft, qc.qubits[:len(unit)])
    qc.barrier()
    #
    
    # Measure
    qc.measure(unit, unit_classical)
    #
    
    # Take a look at the circuit in order to see the gates used
    # print(qc)
    
    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=100)
    count = job.result().get_counts()
    
    # Printed below is the computed cost of the path given the above phase
    # costs and the number of times that value was computed by the circuit
    print(count)
    plot_histogram(count)
    results.append(count)

# Show the count distribution for the measured costs
for result in results:
    ax = plt.axes()
    ax.set_xticklabels(result.keys())
    plt.bar(result.keys(), result.values(), 1.0, color='b')
    plt.show()
    
# Create array of most-occuring costs, should be 3 entries
max_results = []
for elem in results:
    max_count = 0
    cost = ""
    for key, value in elem.items():
        if value > max_count:
            max_count = value
            cost = key
    max_results.append(cost)
print(max_results)
   
# ------- Find path of least cost: Grover's -------
'''
def initialize_s(qc, qubits):
    """
    Apply a H-gate to 'qubits' in qc
    Function from Qiskit textbook
    """
    for q in qubits:
        qc.h(q)
    return qc


# We have a 4-node problem so n = 2
n = 2
grover_circuit = QuantumCircuit(n)
grover_circuit = initialize_s(grover_circuit, [0,1])
grover_circuit.cz(0,1)

# Diffusion operator (U_s)
grover_circuit.h([0,1])
grover_circuit.z([0,1])
grover_circuit.cz(0,1)
grover_circuit.h([0,1])
print(grover_circuit)

# Get the results from the computation
results = job.result()
answer = results.get_counts(grover_circuit)
plot_histogram(answer)
'''
# ------- Find path of least cost: Minimize function -------

# Transform each result into decimal
nums = [0] * len(max_results)
i = 0
for elem in max_results:
    base = 32
    j = 0
    while base >= 1:
        nums[i] += int(elem[j]) * base
        j += 1
        base = base / 2
    i += 1
print(nums)

# Minimize
index = nums.index(min(nums))
print("Which path in the array of eigen_values?", index)

path = eigen_values[index]
print("Path:", path)

print("Corresponds to:", end = " ")

for i in range(0, 8, 2):
    # Grab two digits at a time to translate into the node
    stringg = path[i] + path[i+1]
    print(stringg)
    if stringg == "00":
        print("2", end = "->")
    elif stringg == "01":
        print("4", end = "->")
    elif stringg == "10":
        print("1", end = "->")
    elif stringg == "11":
        print("3", end = "->")
print()

# If you run the classical method with the "simple_graph.txt" file
# then you will get the same path using both the brute force and the 
# nearest neighbor method!


