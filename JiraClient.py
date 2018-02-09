import http.client
import json


class JiraClient():
    board_status_to_env = {"Ready to Deploy": "QAX",
                           "QAX Done": "STGX",
                           "STGX Done": "PROD-EU",
                           "Prod EU Done": "PROD-US",
                           "Prod US Done": "UNKNOWN"}

    def __init__(self, token):
        self.auth_token = token

    def build_headers(self):
        return {
            'Content-Type': "application/json",
            'Authorization': "Basic " + self.auth_token,
            'Cache-Control': "no-cache"
        }

    def fetch_tickets_to_deploy(self):
        conn = http.client.HTTPSConnection("www.mulesoft.org")

        payload = {
            "jql": "project = HX AND issuetype = Story AND status in (\"Ready to Deploy\", \"StgX Done\", \"QAX Done\", \"Prod US Done\", \"Prod EU Done\")",
            "fields": ["summary"]}
        headers = self.build_headers()

        conn.request("POST", "/jira/rest/api/2/search", json.dumps(payload), headers=headers)

        res = conn.getresponse()
        data = res.read()

        # Filter only the tickets required for the current deploy date...
        issues = json.loads(data)['issues']

        return list(map(lambda x: x["key"], issues))

    def fetch_ticket_info(self, id):
        conn = http.client.HTTPSConnection("www.mulesoft.org")

        headers = self.build_headers()
        conn.request("GET", "/jira/rest/api/2/issue/" + id, headers=headers)
        res = conn.getresponse()
        data = res.read()

        return json.loads(data)

    def fetch_subtask_from_id(self, id):
        ticket_info = self.fetch_ticket_info(id)

        subtasks_ids = ticket_info['fields']["subtasks"]
        return list(map(lambda x: x["key"], subtasks_ids))

    def fetch_artifact_from_info(self, sid):
        ticket_info = self.fetch_ticket_info(sid)
        artifact_id = ticket_info["fields"]["components"][0]["name"]
        artifact_version = ticket_info["fields"]["versions"][0]["name"]
        jira_key = ticket_info["key"]

        return {"jira_key": jira_key, "artifact_id": artifact_id, "version": artifact_version}

    def fetch_artifacts(self, date):
        # Fetch all the events ...
        all_stories_keys = self.fetch_tickets_to_deploy()

        # Filter events to be deployed ...
        story_keys = list(
            filter(lambda id: self.fetch_ticket_info(id)["fields"]["customfield_13861"] == date, all_stories_keys))

        # Fetch the first ticket to be deployed ...
        return list(map(lambda sid: self.story_to_deployment_unit(sid), story_keys))

    def story_to_deployment_unit(self, story_key):
        subtask_ids = self.fetch_subtask_from_id(story_key)

        # Fetch artifact version ...
        artifacts = list(map(lambda x: self.fetch_artifact_from_info(x), subtask_ids))

        # Fetch next environment ...
        next_env = self.fetch_next_env_to_deploy(story_key)

        return {"jira_key": story_key, "next_env_to_deploy": next_env, "artifacts": artifacts}

    def move_next_stage(self, id):
        status = self.fetch_ticket_status(id)
        print(status)

    def fetch_ticket_status(self, id):
        # Fetch ticket info ...
        ticket_info = self.fetch_ticket_info(id)
        # Get current state ...
        status = ticket_info["fields"]["status"]["name"]
        return status

    def fetch_next_env_to_deploy(self, sid):
        board_status = self.fetch_ticket_status(sid)
        return self.board_status_to_env[board_status]
