'''
@author: Olivia Pitcl
Phys 305, K Johns
Creative Project

An implementation of the travelling salesman problem
using the classical methodologies.

https://en.wikipedia.org/wiki/Travelling_salesman_problem#Computing_a_solution
'''

    
def heuristic(nodes, start):
    '''
    Finds shortest path between the given list of
    locations and finds the shortest path amongst them,
    visiting one node once and ending at the starting
    node.
    '''
    return

def build_tree(root, list_cities, dict_cities):
    '''
    Builds a tree given a root node and a set of the remaining
    city nodes.
    
    @param 
        Node root, root of tree
        list of Nodes list_cities, list of nodes
        dictionary (String, list of floats) dict_cities
        
    @return
        Node root, linked to built tree
    '''
    print("current city:", root.city)
    
    if len(dict_cities) == 0:
        return root
    
    # Grab lengths of cities connected to root node
    distances = dict_cities[root.city]
    
    # Loop through cities and add edges to root node
    for j in range(len(distances)):
        if distances[j] != 0:
            res = root.add_edge(list_cities[j], distances[j])
    print("root edges")
    root.print_edges()
    
    # Remove root city from dict so it's not added to subtree
    # Recurse and make tree from each node
    
    del dict_cities[root.city]
    if root in list_cities:
        i = list_cities.remove(root)
    for elem in root.edges:
        build_tree(elem, list_cities, dict_cities) 
    list_cities.insert(i, root)
    return root

    

def read_nodes(file_name):
    '''
    Reads in a file and makes a root node and a set of
    nodes with the remaining cities. Calls a function that
    builds the tree from the root node.
    
    @return Node, root linked to built tree
    '''
    file = open(file_name, "r")
    print("opening file", file_name + "\n")
    cities = file.readline().strip().split()
    list_cities = []
    
    # Grab root node and index
    # We can use index to access distances for the first tier
    # Add the rest of the cities to the set
    print(cities)
    root = input("Give starting point from the cities above\n")
    for i in range(len(cities)):
        if cities[i] == root:
            root = Node(cities[i])
        list_cities.append(Node(cities[i]))
    
    # Link edges
    info = file.readlines()
    
    dict_cities = {}
    for line in info:
        line = line.strip().split()
        dist = []
        for elem in line[1:]:
            dist.append(float(elem))
        dict_cities[line[0]] = dist
    
    file.close()
    
    return build_tree(root, list_cities, dict_cities)


def print_edges(root):
    if len(root.edges) == 0:
        print(root, end = "")
        return
    
    print("root:", root, "-> ", end = "")
    
    for elem in root.edges:
        print_edges(elem)
    print()


def main():
    root = read_nodes("simple_graph.txt")
    print_edges(root)




# Each class will have a dictionary of other Nodes it
# is connected to, each node having their own coordinate
# tuples
class Node:
    '''
    Node class, containing its own location and a dictionary
    mapping the node to each location via an edge length
    
    '''
    def __init__(self, city):
        self.city = city
        self.edges = {}
    
    def equals(self, node):
        return (self.city == node.city)
    
    def __str__(self):
        print("City: " + str(self.city))
        
    def print_edges(self):
        print("{ ", end = "")
        for key, value in self.edges.items():
            print(key.city + " : ", end = "")
            print(value, end = ", ")
        print(" }")
        
    def add_edge(self, node, edge):
        if not type(node) == Node:
            print("Error, must add Node object to edges, not", type(node))
            return -1
        self.edges[node] = edge

main()


