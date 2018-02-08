import requests
import base64
import yaml
import sys

if len(sys.argv) != 2:
	print "Github bot not invoked correctly. Need github Access Token"
	sys.exit()

githubAccessToken = sys.argv[1]
repos = ['popeye_appviz']

for repo in repos:
	r = requests.get('https://api.github.com/repos/mulesoft-labs/' + repo + '/contents/popeye.yaml?access_token=' + githubAccessToken)
	if r.status_code == 200:
		data = r.json()['content']
		yaml_content = yaml.load(base64.b64decode(data))
		print("Found Popeye Yaml for " + repo)
		for dependency in yaml_content['require']:
			srcNode = repo
			destNode = dependency
			print("Found a dependency from " + srcNode + " - " + destNode)
			# TODO: Invoke Neo4j API Here
	else:
		print("Error in reading from github for " + repo)
		print("Status Code: " + str(r.status_code))