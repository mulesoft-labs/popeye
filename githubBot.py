import requests
import base64
import yaml
import sys
import logging

from persistor import persistor

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%b/%d/%Y %H:%M:%S %Z',
					level=logging.INFO)

if len(sys.argv) != 5:
    print "Github bot not invoked correctly. Need github Access Token"
    sys.exit()

githubAccessToken = sys.argv[1]
n4jUrl = sys.argv[2]
n4jUser = sys.argv[3]
n4jpwd = sys.argv[4]
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
				persistor.createServiceDependency(me, dependency)
		else:
			persistor.createServiceDependency(me, None)