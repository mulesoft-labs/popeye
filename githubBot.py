import requests
import base64
import yaml
import logging
import argparse

from persistor import persistor

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%b/%d/%Y %H:%M:%S %Z',
					level=logging.INFO)

def addToAdjacencyList(dest, src):
	if src not in adjacencyList:
		adjacencyList[src] = []
	if dest not in adjacencyList:
		adjacencyList[dest] = []
	adjacencyList[src].append(dest)

def writeAdjacencyListToFile():
	f = open('adjacency_list.txt', 'w')
	for node in adjacencyList:
		f.write(node + " " + ','.join(adjacencyList[node]) + '\n')
	f.close()

parser = argparse.ArgumentParser()
parser.add_argument("-gt", "--githubAccessToken", required=True)
parser.add_argument("-nl", "--n4jUrl", required=True)
parser.add_argument("-nu", "--n4jUser", required=True)
parser.add_argument("-np", "--n4jpwd", required=True)
args = parser.parse_args()
githubAccessToken = args.githubAccessToken
n4jUrl = args.n4jUrl
n4jUser = args.n4jUser
n4jpwd = args.n4jpwd
adjacencyList = {}
repos = ['popeye_appviz', 'popeye_appviz_ui', 'popeye_cloudhub_platform', 'popeye_coreservices', 'popeye_exchange', 'popeye_anypoint_ui']
persistor = persistor(url=n4jUrl, username=n4jUser, pwd=n4jpwd, logger=logger)

for repo in repos:
	logger.info("Scanning github dependencies for {}".format(repo))
	r = requests.get('https://api.github.com/repos/mulesoft-labs/' + repo + '/contents/popeye.yaml?access_token=' + githubAccessToken)
	data=None
	if r.status_code == 200:
		data = r.json()['content']
	elif r.status_code == 404:
		logger.error("No yaml dependency file found for " + repo)
	else:
		logger.error("Error in reading from github for " + repo + ".Status Code: " + str(r.status_code))

	if data:
		yaml_content = yaml.load(base64.b64decode(data))
		logger.info("Found popeye.yaml for github repo:" + repo)
		if yaml_content.has_key('id'):
			me = {'id':yaml_content['id']}
		else:
			me = {'id': repo}
		if yaml_content.has_key('deploy_build'):
			me['deploy_build'] = yaml_content['deploy_build']
		if yaml_content.has_key('require'):
			for dependency in yaml_content['require']:
				logger.info("Found a dependency from " + me['id'] + " -> " + dependency)
				addToAdjacencyList(me['id'], dependency)
				persistor.createServiceDependency(me, dependency)
		else:
			persistor.createServiceDependency(me, None)

writeAdjacencyListToFile()
