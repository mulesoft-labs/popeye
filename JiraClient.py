import http.client
import json


class JiraClient():
    def __init__(self, token):
        self.auth_token = token

    def build_headers(self):
        return {
            'Content-Type': "application/json",
            'Authorization': "Basic " + self.auth_token,
            'Cache-Control': "no-cache"
        }

    def fetch_tickets_ready_to_deploy(self):
        conn = http.client.HTTPSConnection("www.mulesoft.org")

        payload = {"jql": "project = HX AND issuetype = Story AND status = \"Ready to Deploy\"", "fields": ["summary"]}
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

        subtasksIds = ticket_info['fields']["subtasks"]
        return list(map(lambda x: x["key"], subtasksIds))

    def fetch_artifact_from_info(self, sid):
        ticket_info = self.fetch_ticket_info(sid)
        artifact_id = ticket_info["fields"]["components"][0]["name"]
        artifact_version = ticket_info["fields"]["versions"][0]["name"]
        return {"id": artifact_id, "version": artifact_version}

    def fetch_artifacts(self, date):
        # Fetch all the events ...
        stories_keys = self.fetch_tickets_ready_to_deploy()

        storiesKey = list(
            filter(lambda id: self.fetch_ticket_info(id)["fields"]["customfield_13861"] == date, stories_keys))

        if len(storiesKey) != 1:
            raise ValueError("0 or more tickets to deploy in the same day")

        # Fetch the first ticket to be deployed ...
        subtasksIds = self.fetch_subtask_from_id(storiesKey[0])

        # Fetch artifact Version ...
        return list(map(lambda x: self.fetch_artifact_from_info(x), subtasksIds))
