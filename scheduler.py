import logging
import JiraClient
from PopEyeGenJenkins import PopEyeGenJenkins
import time
import argparse
import random

from db import db

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%b/%d/%Y %H:%M:%S %Z', level=logging.INFO)

class scheduler(object):
	def __init__(self, **kwargs):
		url = kwargs['url']
		username = kwargs['username']
		pwd = kwargs['pwd']
		self.db = db(url=url, username=username, pwd=pwd, logger=logger)
		self.client = JiraClient.JiraClient(kwargs['jiraAccessToken'])
		logger.debug("scheduler initialized. url={0} username={1} pwd={2}".format(url, username, pwd))

	def getDeployableComponents(self):
		deployTickets = self.client.fetch_artifacts(time.strftime("%Y-%m-%d"))
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

	def generateDeploymentOrder(self, order, deployableComponents):
		artifactComponentMap = {}
		graph = self.db.getGraph()
		graph2 = self.db.getGraph2()
		for component in deployableComponents:
			artifactComponentMap[component['artifact_id']] = component
		deploymentOrder = []
		for artifact in order:
			if artifact in artifactComponentMap:
				for dep in graph2[artifact]:
					if dep not in artifactComponentMap:
						comment = str(artifactComponentMap[artifact]['jira_key']) + ": Unable to continue deploy. " + str(dep) + " is required to deploy " + str(artifact)
						self.client.update_comment(artifactComponentMap[artifact]['jira_key'], comment)
						print comment
						return None
				requestedVersion = artifactComponentMap[artifact]['version']
				for dependentArtifact in graph[artifact]:
					if dependentArtifact in artifactComponentMap.keys():
						dependentVersion = self.db.getDependencyVersion(artifact, dependentArtifact)
						if requestedVersion != dependentVersion:
							comment = str(artifactComponentMap[artifact]['jira_key']) + ": Unable to continue deploy. Version of " + str(artifact) + " is not compatible for this release"
							print comment
							self.client.update_comment(artifactComponentMap[artifact]['jira_key'], comment)
							return None
				artifactComponentMap[artifact]['deployBuild'] = str(self.db.getDeployBuild(artifact))
				artifactComponentMap[artifact]['smokeBuild'] = str(self.db.getSmokeBuild(artifact))
				deploymentOrder.append(artifactComponentMap[artifact])
		return deploymentOrder

	def invokeDeploymentPipeline(self):
		order = self.db.queryNodesInTopologicalOrder()
		for deployableComponent in self.getDeployableComponents():
			deploymentOrder = self.generateDeploymentOrder(order, deployableComponent['artifacts'])
			if deploymentOrder is not None:
				poppyJenkObj = PopEyeGenJenkins(deployableComponent['env'])
				poppyJenkObj.startDeploy(deployableComponent['jira_key'], deploymentOrder)
				print deployableComponent['jira_key']
				print deployableComponent['env']
				print deploymentOrder
			else:
				print "Aborted deploy of " + str(deployableComponent['jira_key'])


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-jt", "--jiraAccessToken", required=True)
	parser.add_argument("-nl", "--n4jUrl", required=True)
	parser.add_argument("-nu", "--n4jUser", required=True)
	parser.add_argument("-np", "--n4jpwd", required=True)
	args = parser.parse_args()
	scheduler = scheduler(url=args.n4jUrl, username=args.n4jUser, pwd=args.n4jpwd, jiraAccessToken=args.jiraAccessToken)
	scheduler.invokeDeploymentPipeline()
