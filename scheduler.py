from collections import deque

def getGraph():
	adjacencyList = {}
	f = open('adjacency_list.txt')
	for line in iter(f):
		data = line.strip().split(" ")
		if data[0] not in adjacencyList:
			adjacencyList[data[0]] = []
		if len(data) == 1:
			continue
		for node in data[1].split(','):
			adjacencyList[data[0]].append(node)
	return adjacencyList

def kahn_topsort(graph):
    in_degree = { u : 0 for u in graph }     # determine in-degree 
    for u in graph:                          # of each node
        for v in graph[u]:
            in_degree[v] += 1
 
    Q = deque()                 # collect nodes with zero in-degree
    for u in in_degree:
        if in_degree[u] == 0:
            Q.appendleft(u)
 
    L = []     # list for order of nodes
     
    while Q:                
        u = Q.pop()          # choose node of zero in-degree
        L.append(u)          # and 'remove' it from graph
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                Q.appendleft(v)
 
    if len(L) == len(graph):
        return L
    else:                    # if there is a cycle,  
        return []            # then return an empty list

order = kahn_topsort(getGraph())