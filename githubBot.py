import requests
import base64

repos = ['popeye_appviz']

for repo in repos:
	r = requests.get('https://api.github.com/repos/mulesoft-labs/' + repo + '/contents/popeye.yaml?access_token=6d0e88b8de7f168b4bd4d410be97b3a3148e547e')
	if r.status_code == 200:
		data = r.json()['content']
		str = base64.b64decode(data)
		print("Popeye Yaml for " + repo)
		print(str + '\n')
	else:
		print("Error in reading from github for " + repo)
		print("Status Code: " + str(r.status_code))
