from flask import Flask, request, abort, jsonify
from JiraClient import JiraClient
import json

application = Flask(__name__)
client = JiraClient("aGFja3gudXNlcjpoYWNreC51c2VyTXVsZTE =")

@application.route('/mbis/', methods=['GET'])
def getMbis():
    stories = client.fetch_stories()
    print stories
    return jsonify(stories)

@application.route('/mbis/<mbiID>', methods=['GET'])
def getSpecificMbi(mbiID):
    artifact = client.story_to_deployment_unit(mbiID)
    return jsonify(artifact.get('artifacts'))

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080, debug=False)
