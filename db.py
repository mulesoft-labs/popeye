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
        if 'deploy_build' in _this:
            _this_deploy_build = _this['deploy_build']
            self.n4j.query(q="MERGE (node:artifact {name: '" + _this_name + "'}) set node.deploy_build='"+_this_deploy_build+"' RETURN node")
        else:
            self.n4j.query(q="MERGE (node:artifact {name: '" + _this_name + "'}) RETURN node")
        if _that:
            self.n4j.query(q="MERGE (node:artifact {name: '" + _that + "'}) RETURN node")
            self.n4j.query(q="MATCH (a:artifact), (b:artifact) WHERE a.name='"+_this_name+"' AND b.name='"+_that+ "' CREATE UNIQUE (a)<-[:dependency_of]-(b)")
            self.logger.info("inserted relation into db.({})<-dependency_of-({})".format(_this_name, _that))

    def clearAllNodes(self):
        self.n4j.query(q="MATCH (n), ()-[r]-() DELETE n,r")

    def queryNodesInTopologicalOrder(self):
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