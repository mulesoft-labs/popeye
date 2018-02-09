import requests
import base64
import yaml
import sys
import logging

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

if len(sys.argv) != 5:
    print "Github bot not invoked correctly. Need github Access Token"
    sys.exit()

adjacencyList = {}
githubAccessToken = sys.argv[1]
n4jUrl = sys.argv[2]
n4jUser = sys.argv[3]
n4jpwd = sys.argv[4]
repos = ['popeye_appviz', 'popeye_appviz_ui', 'popeye_cloudhub_platform', 'popeye_coreservices', 'popeye_exchange', 'popeye_anypoint_ui']
persistor = persistor(url=n4jUrl, username=n4jUser, pwd=n4jpwd, logger=logger)

logger.info("Scanning github dependencies...")
for repo in repos:
	r = requests.get('https://api.github.com/repos/mulesoft-labs/' + repo + '/contents/popeye.yaml?access_token=' + githubAccessToken)
	if r.status_code == 200:
		data = r.json()['content']
		yaml_content = yaml.load(base64.b64decode(data))
		logger.info("Found popeye.yaml for github repo:" + repo)
		for dependency in yaml_content['require']:
			me = repo
			logger.info("Found a dependency from " + me + " -> " + dependency)
			addToAdjacencyList(me, dependency)
			persistor.createServiceDependency(me, dependency)
	elif r.status_code == 404:
		logger.error("No yaml dependency file found for " + repo)
	else:
		logger.error("Error in reading from github for " + repo + ".Status Code: " + str(r.status_code))
	writeAdjacencyListToFile()

