#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Olivia Pitcl

Phys 305, Creative Project

Program to solve the travelling salesmand problem
in the classical method (brute force and nearest neighbor).
"""

import time
import random

def dict_edges():
    '''
    Produces a dictionary mapping a tuple of strings (0th index is
    from, 1st is to)
    
    Dictionary will look like:
        {('Tallahassee', 'Phoenix'): 20, ('Miami', 'Phoenix'), 50}
        Meaning it takes 20 units to travel from Tallahassee to Phoenix
    '''
    file = open("simple_graph.txt", "r")
    edges = {}
    start_nodes = file.readline().strip().split()
    nodes = file.readlines()
    
    # Loop through file data
    for end in nodes:
        end = end.strip().split()
        vert = end[0]
        i = 0
        # Loop through the costs in the file's matrix
        for cost in end[1:]:
            if not start_nodes[i] == vert:
                vertices = (start_nodes[i], vert)
                edges[vertices] = float(cost)
            i += 1
    file.close()
    return edges

def random_edges(n):
    '''
    Produces a randomized dictionary of vertices using the same
    format as above, except each tuple of city-to-city is encoded as
    seperate numbers 0 through n-1.
    '''
    edges = {}
    for i in range(n):
        for j in range(i, n):
            vertex_1 = (str(i), str(j))
            vertex_2 = (str(j), str(i))
            cost = random.randint(1, 10)
            if (i == j):
                cost = 0
            edges[(vertex_1)] = cost
            edges[(vertex_2)] = cost
    return edges

def nearest_neighbor(start, edges, n):
    '''
    Given the dictionary of vertices, a starting point, and the number of
    cities in the dictionary, approximates the shortest path of travel between
    all cities.
    
    Runtim is O(n^2) since we have two for-loops.
    '''
    cur = start
    next_cur = cur
    cost = 0
    cur_cost = 0
    used = []
    used.append(cur)
    for i in range(n-1):
        # Set initial minimum to maximum as seen in randomized
        # dictionary function above
        minimum = 11
        
        # Find the node we want to travel to next
        for key, value in edges.items():
            # Find the node pair with the smallest cost
            if (key[0] == cur) and (not key[1] in used) and value < minimum:
                minimum = value
                cur_cost = value
                cur = next_cur
                
                # Place the next node we just found
                next_cur = key[1]
                used.append(next_cur)
        cost += cur_cost
        
    last = used[len(used) - 1]
    # Find path from last node back to beginning
    for key, value in edges.items():
        if key[0] == last and key[1] == start:
            cost += value
            used.append(start)
    # Used has the order of nodes, cost is the total cost of travel
    return used, cost

def edges_2d(edges, n):
    '''
    Takes in the dictionary produced either randomly or through a file
    and produces a n x n matrix of path costs from city 0 to city n-1. 
    It will look like this:
        
        for 3 cities:
            0   1   2
        0   0   4   7
        1   4   0   8
        2   7   8   0
    '''
    result = []
    for i in range(n):
        result.append([0] * n)
    for pair, cost in edges.items():
        # **NOTE** if you run this with the randomized edges
        # instead you need to take of the -1
        # If you run this with the national parks file this function
        # will have to change a lot, since I changed it to make it
        # conducive to the randomized trials after running the national
        # parks file
        i = int(pair[0]) - 1
        j = int(pair[1]) - 1
        result[i][j] = cost
    return result
            

def brute_force(cur, cities, costs, count, cost, minimum):
    '''
    Loop through all possible paths to find the lowest cost.
    Number of nodes is length of cities.
    '''
    # Base case of recursive function
    # If we've found our last node and the value of its
    # cost to the start is nonzero
    if (count == len(cities) - 1):
        # Add return cost
        cost += costs[cur][0]
        # Minimize
        if cost < minimum:
            minimum = cost
        else:
            cost -= costs[cur][0]
        return minimum
    
    for i in range(len(cities)):
        # If city has not been visited and cost of edge is nonzero
        if (cities[i] == False):
            # Visit ith city
            cities[i] = True
            # result.append(i)
            minimum = brute_force(i, cities, costs, count + 1, cost + costs[cur][i], minimum)
            # result.remove(i)
            # Unvisit ith city
            cities[i] = False
    return minimum
    

def main():
    total_time_nn = 0
    total_time_bf = 0
    
    # Initial conditions. Feel free to change around to find runtime results
    iterations = 1
    num_edges = 4
    start = '1'
    
    # Runs n trials of the nearest neighbor method and brute force
    for i in range(iterations):
        edges = dict_edges()
        # print(edges)
        
        # Nearest Neighbor
        time_1 = time.perf_counter_ns()
        used_nn, cost_nn = nearest_neighbor(start, edges, num_edges)
        total_time_nn += time.perf_counter_ns() - time_1
        
        # Resukts of iteration i
        print(used_nn)
        # print(cost_nn)
        
        # Brute Force
        edges_matrix = edges_2d(edges, num_edges)
        # print(edges_matrix)
        cost_bf = 0
        minimum = 100
        
        # Vertices represents which cities 0 through n-1 is false
        vertices = []
        for i in range(num_edges):
            vertices.append(False)
        vertices[0] = True
        
        # Start timer
        time_2 = time.perf_counter_ns()
        
        # Initialize function with initial position, visited status, 
        # matrix of costs, count = 0, cost = 0, and a high minimum to be
        # calculated
        minimum = brute_force(int(start), vertices, edges_matrix, 0, cost_bf, minimum)
        total_time_bf += time.perf_counter_ns() - time_2
        
        # Results of iteration i
        # print(used_bf)
        # print(minimum)
        
    print("Nearest neighbor time:", total_time_nn / iterations)
    print("Brute force time:", total_time_bf / iterations)
    

main()