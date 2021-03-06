#! /usr/bin/env python

from neo4jrestclient.client import GraphDatabase
from collections import deque


class db(object):
    def __init__(self, **kwargs):
        url = kwargs['url']
        username = kwargs['username']
        pwd = kwargs['pwd']

        self.n4j = GraphDatabase(url, username=username, password=pwd)

        self.logger = kwargs['logger']
        self.logger.debug("Neo4j initialized. url={0} username={1} pwd={2}".format(url, username, pwd))

    def createServiceDependency(self, _this, _that):
        #_this is a complex object
        _this_name = _this['id']
        self.n4j.query(q="MERGE (node:artifact {name: '" + _this_name + "'}) RETURN node")
        if 'deploy_build' in _this:
            self.n4j.query(q="MERGE (node:artifact {name: '" + _this_name + "'}) set node.deploy_build='" + _this[
                'deploy_build'] + "' RETURN node")
        if 'smoke_build' in _this:
            self.n4j.query(q="MERGE (node:artifact {name: '" + _this_name + "'}) set node.smoke_build='" + _this[
                'smoke_build'] + "' RETURN node")
        if _that:
            name = _that['name'] if 'name' in _that else _that
            version = _that['version'] if 'version' in _that else "UNKNOWN"
            self.n4j.query(q="MERGE (node:artifact {name: '" + name + "'}) RETURN node")
            self.n4j.query(q="MATCH (a:artifact), (b:artifact) WHERE a.name='"+_this_name+"' AND b.name='"+name+ "' CREATE UNIQUE (a)<-[r:dependency_of]-(b) SET r.version='"+version+"'")
            self.logger.info("inserted relation into db.({})<-dependency_of-({})".format(_this_name, name))

    def clearAllNodes(self):
        self.n4j.query(q="MATCH (n), ()-[r]-() DELETE n,r")

    def getGraph(self):
        graph={}
        for tuple in self.n4j.query(q='MATCH (n)-[r]->(m) RETURN n.name,m.name').elements:
            node = tuple[0]
            dependsOnNode = tuple[1]
            if node not in graph:
                graph[node] = []
            if dependsOnNode not in graph:
                graph[dependsOnNode] = []
            if dependsOnNode not in graph[node]:
                graph[node].append(dependsOnNode)
	return graph

    def getGraph2(self):
        graph={}
        for tuple in self.n4j.query(q='MATCH (n)-[r]->(m) RETURN n.name,m.name').elements:
            node = tuple[0]
            dependsOnNode = tuple[1]
            if node not in graph:
                graph[node] = []
            if dependsOnNode not in graph:
                graph[dependsOnNode] = []
            if node not in graph[dependsOnNode]:
                graph[dependsOnNode].append(node)
        return graph

    def queryNodesInTopologicalOrder(self):
        graph = self.getGraph()
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

    def getDeployBuild(self, artifact):
        result = self.n4j.query(q="match(n) where n.name=\'" + str(artifact) + "\' return n.deploy_build")
        return result[0][0]

    def getDependencyVersion(self, _this, _that):
        #_this----dependency_of--->_that
        result = self.n4j.query(q="match (n:artifact {name:'"+_this+"'})-[r]->(m:artifact {name:'"+_that+"'})  return r.version;")
        return result[0][0]

    def getSmokeBuild(self, artifact):
        result = self.n4j.query(q="match(n) where n.name=\'" + str(artifact) + "\' return n.smoke_build")
        return result[0][0]

#TODO : no circular dependency.
# self.n4j.query(q="MERGE (serviceThis)-[:dependsOn {r:'dependsOn'}]->(serviceThat)")
# MERGE (n)-[:know {r:'123'}]->(test2) //Create the relation between these nodes if it does not already exist
# serviceThis = self.n4j.node(name=_this)
# serviceThat = self.n4j.node(name=_dependsOn)
# serviceThis.relationships.create("depends_on", serviceThat)
#
#
#q = 'MATCH (u:User)-[r:likes]->(m:Beer) WHERE u.name="Marco" RETURN u, type(r), m'
# "db" as defined above
# results = db.query(q, returns=(client.Node, str, client.Node))
#for r in results:
#    print("(%s)-[%s]->(%s)" % (r[0]["name"], r[1], r[2]["name"
#
#
# # Create some nodes with labels
# user = db.labels.create("User")
# u1 = db.nodes.create(name="Marco")
# user.add(u1)
# u2 = db.nodes.create(name="Daniela")
# user.add(u2)
#
# beer = db.labels.create("Beer")
# b1 = db.nodes.create(name="Punk IPA")
# b2 = db.nodes.create(name="Hoegaarden Rosee")
# # You can associate a label with many nodes in one go
# beer.add(b1, b2)
#
# # User-likes->Beer relationships
# u1.relationships.create("likes", b1)
# u1.relationships.create("likes", b2)
# u2.relationships.create("likes", b1)
# # Bi-directional relationship?
# u1.relationships.create("friends", u2)
