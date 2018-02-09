import argparse

from flask import Flask, jsonify
from JiraClient import JiraClient

from scheduler import scheduler

parser = argparse.ArgumentParser()
parser.add_argument("-jt", "--jiraAccessToken", required=True)
parser.add_argument("-nl", "--n4jUrl", required=True)
parser.add_argument("-nu", "--n4jUser", required=True)
parser.add_argument("-np", "--n4jpwd", required=True)
args = parser.parse_args()

application = Flask(__name__)
client = JiraClient(args.jiraAccessToken)
s = scheduler(url=args.n4jUrl, username=args.n4jUser, pwd=args.n4jpwd, jiraAccessToken=args.jiraAccessToken)

@application.route('/mbis/', methods=['GET'])
def getMbis():
    stories = client.fetch_stories()
    print(stories)
    return jsonify(stories)

@application.route('/mbis/<mbiID>', methods=['GET'])
def getSpecificMbi(mbiID):
    artifact = client.story_to_deployment_unit(mbiID)
    return jsonify(artifact.get('artifacts'))

@application.route('/mbis/<id>/nextStage', methods=['PUT'])
def moveMbi(id):
    client.move_next_stage(id)
    return "done"

@application.route('/scheduler', methods=['POST'])
def scheduler():
    s.invokeDeploymentPipeline()
    return "done"

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080, debug=False)