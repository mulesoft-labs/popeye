from collections import deque
import JiraClient
from neo4jrestclient.client import GraphDatabase
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-jt", "--jiraAccessToken", required=True)
parser.add_argument("-nl", "--n4jUrl", required=True)
parser.add_argument("-nu", "--n4jUser", required=True)
parser.add_argument("-np", "--n4jpwd", required=True)
args = parser.parse_args()
gdb = GraphDatabase(args.n4jUrl, username=args.n4jUser, password=args.n4jpwd)
jiraAccessToken = args.jiraAccessToken

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

def getDeployableComponents():
	token = jiraAccessToken
	client = JiraClient.JiraClient(token)
	deployTickets = client.fetch_artifacts(time.strftime("%Y-%m-%d"))
	deployableComponents = []
	for ticket in deployTickets:
		for artifact in ticket['artifacts']:
			deployableComponents.append(artifact)
	return deployableComponents

def generateDeploymentOrder(order, deployableComponents):
	artifactComponentMap = {}
	for component in deployableComponents:
		artifactComponentMap[str(component['artifact_id'])] = component
	deploymentOrder = []
	for artifact in order:
		if artifact in artifactComponentMap:
			query = "match(n) where n.name=\'" + str(artifact) + "\' return n.deploy_build"
			result = gdb.query(query)
			artifactComponentMap[artifact]['deployBuild'] = str(result[0][0])
			deploymentOrder.append(artifactComponentMap[artifact])
	return deploymentOrder

order = kahn_topsort(getGraph())
componentsToBeDeployed = getDeployableComponents()
deploymentOrder = generateDeploymentOrder(order, componentsToBeDeployed)
print deploymentOrder
