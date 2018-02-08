#! /usr/bin/env python

#from neo4j.v1 import GraphDatabase
from neo4jrestclient.client import GraphDatabase


class persistor(object):
    def __init__(self, **kwargs):
        url = kwargs['url']
        username = kwargs['username']
        pwd = kwargs['pwd']
        #n4j = GraphDatabase("http://127.0.0.1:7474", username="neo4j", password="popeye")
        #db = GraphDatabase("http://localhost:7474", username="neo4j", password="mypassword")

        self.n4j = GraphDatabase(url, username=username, password=pwd)

        self.logger = kwargs['logger']
        self.logger.debug("Neo4j initialized. url={0} username={1} pwd={2}".format(url, username, pwd))

    def createServiceDependency(self, _this, _dependsOn):
        serviceThis = self.n4j.node(name=_this)
        serviceThat = self.n4j.node(name=_dependsOn)
        serviceThis.relationships.create("depends_on", serviceThat)



#TODO : no circular dependency.
#
#
#
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