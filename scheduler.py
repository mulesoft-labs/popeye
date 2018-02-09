import logging
from collections import deque
import JiraClient
from neo4jrestclient.client import GraphDatabase
from PopEyeGenJenkins import PopEyeGenJenkins
import time
import argparse
import random

from db import db

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%b/%d/%Y %H:%M:%S %Z', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-jt", "--jiraAccessToken", required=True)
parser.add_argument("-nl", "--n4jUrl", required=True)
parser.add_argument("-nu", "--n4jUser", required=True)
parser.add_argument("-np", "--n4jpwd", required=True)
args = parser.parse_args()
# gdb = GraphDatabase(args.n4jUrl, username=args.n4jUser, password=args.n4jpwd)

db = db(url=args.n4jUrl, username=args.n4jUser, pwd=args.n4jpwd, logger=logger)

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
	client = JiraClient.JiraClient(jiraAccessToken)
	deployTickets = client.fetch_artifacts(time.strftime("%Y-%m-%d"))
	deployableComponents = []
	for ticket in deployTickets:
		deployableComponent = {}
		deployableComponent['jira_key'] = ticket['jira_key']
		deployableComponent['env'] = ticket['next_env_to_deploy']
		for artifact in ticket['artifacts']:
			artifact['deploy_time'] = random.randint(1,10)
			artifact['test_time'] = random.randint(1,10)
			artifact['deploy_success'] = True
			artifact['test_success'] = True
			if 'artifacts' not in deployableComponent:
				deployableComponent['artifacts'] = []
			deployableComponent['artifacts'].append(artifact)
		deployableComponents.append(deployableComponent)
	return deployableComponents

def generateDeploymentOrder(order, deployableComponents):
	artifactComponentMap = {}
	for component in deployableComponents:
		artifactComponentMap[str(component['artifact_id'])] = component
	deploymentOrder = []
	for artifact in order:
		if artifact in artifactComponentMap:
			# query = "match(n) where n.name=\'" + str(artifact) + "\' return n.deploy_build"
			# result = gdb.query(query)
			# artifactComponentMap[artifact]['deployBuild'] = str(result[0][0])
			artifactComponentMap[artifact]['deployBuild'] = db.getDeployBuild(artifact)
			deploymentOrder.append(artifactComponentMap[artifact])
	return deploymentOrder

def invokeDeploymentPipeline(order, deployableComponents):
	for deployableComponent in deployableComponents:
		deploymentOrder = generateDeploymentOrder(order, deployableComponent['artifacts'])
		poppyJenkObj = PopEyeGenJenkins(deployableComponent['env'])
		poppyJenkObj.startDeploy(deployableComponent['jira_key'], deploymentOrder)
		print deployableComponent['jira_key']
		print deployableComponent['env']
		print deploymentOrder

order = kahn_topsort(getGraph())
#deploymentOrder = generateDeploymentOrder(order, componentsToBeDeployed)
deploymentOrder = generateDeploymentOrder(db.queryNodesInTopologicalOrder(), getDeployableComponents())
print deploymentOrder
componentsToBeDeployed = getDeployableComponents()
invokeDeploymentPipeline(order, componentsToBeDeployed)
