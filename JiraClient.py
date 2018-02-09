import json, requests, subprocess


class JiraClient():
    board_status_to_env = {"Ready to Deploy": "QAX",
                           "QAX Done": "STGX",
                           "StgX Done": "PROD-EU",
                           "Prod EU Done": "PROD-US",
                           "Prod US Done": "UNKNOWN"}

    env_to_status_id = {"QAX": "21", "STGX": "31", "PROD-EU": "41", "PROD-US": "51"}

    def __init__(self, token):
        self.auth_token = token

    def build_headers(self):
        return {
            'Content-Type': "application/json",
            'Authorization': "Basic " + self.auth_token,
            'Cache-Control': "no-cache"
        }

    def fetch_tickets_to_deploy(self):
        payload = {
            "jql": "project = HX AND issuetype = Story AND status in (\"Ready to Deploy\", \"StgX Done\", \"QAX Done\", \"Prod EU Done\")",
            "fields": ["summary"]}
        headers = self.build_headers()
        url = 'https://www.mulesoft.org/jira/rest/api/2/search'
        r = requests.post(url, data=json.dumps(payload), headers=headers)

        # Filter only the tickets required for the current deploy date...
        issues = r.json()['issues']
        return list(map(lambda x: x["key"], issues))

    def fetch_ticket_info(self, id):
        headers = self.build_headers()
        url = 'https://www.mulesoft.org/jira/rest/api/2/issue/' + id
        r = requests.get(url, headers=headers)
        return r.json()

    def fetch_subtask_from_id(self, id):
        ticket_info = self.fetch_ticket_info(id)

        subtasks_ids = ticket_info['fields']["subtasks"]
        return list(map(lambda x: x["key"], subtasks_ids))

    def fetch_artifact_from_info(self, sid):
        ticket_info = self.fetch_ticket_info(sid)
        comp = ticket_info["fields"]["components"]

        # Fetch component ...
        if len(comp) == 0:
            raise ValueError(sid + " must have component defined")
        artifact_id = comp[0]["name"]

        # Fetch version ...
        version = ticket_info["fields"]["versions"]
        if len(version) ==0:
            raise ValueError(sid + " must have version defined")
        artifact_version = version[0]["name"]

        if len(comp) == 0:
            raise ValueError(sid + " must have version defined")

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

    def move_next_stage(self, sid):
        # Fetch ticket status ...
        board_status = self.fetch_ticket_status(sid)
        print(board_status)

        next_status = self.board_status_to_env[board_status]

        # Move ticket to a new status ...
        status_id = self.env_to_status_id[next_status]

        payload = {
            "update": {
                "comment": [
                    {
                        "add": {
                            "body": "Automatic flow transitioning based on flow"
                        }
                    }
                ]
            },
            "transition": {
                "id": status_id
            }
        }

        headers = self.build_headers()
        url = 'https://www.mulesoft.org/jira/rest/api/2/issue/' + sid + '/transitions'
        print(payload)

        # Move to next status ...
        requests.post(url, data=json.dumps(payload), headers=headers)

    def description_commit(self):
        pull = "git pull"
        diff = "git diff HEAD^ HEAD"
        processPull = subprocess.Popen(pull.split(), stdout=subprocess.PIPE)
        output, error = processPull.communicate()
        if (error is None):
            processDiff = subprocess.Popen(diff.split(), stdout=subprocess.PIPE)
            output, error = processDiff.communicate()
            if (error is None):
                return str(output)
            else:
                print
                str(error)
        else:
            print
            str(error)

    def create_subtask(self, summary, description):
        project = input("Enter project: ")
        issue = input("Enter MBI: ")
        payload = {
            "fields":
                {
                    "project":
                        {
                            "key": project
                        },
                    "parent":
                        {
                            "key": issue
                        },
                    "summary": summary,
                    "description": description,
                    "issuetype":
                        {
                            "name": "Sub-task"
                        }
                }
        }
        headers = self.build_headers()
        url = 'https://www.mulesoft.org/jira/rest/api/2/issue/'
        r = requests.post(url, data=json.dumps(payload), headers=headers)