import http.client
import json


def build_headers():
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Basic xxxx",
        'Cache-Control': "no-cache"
    }
    return headers


def fetch_tickets_ready_to_deploy():
    conn = http.client.HTTPSConnection("www.mulesoft.org")

    payload = {"jql": "project = HX AND issuetype = Story AND status = \"Ready to Deploy\"", "fields": ["summary"]}
    headers = build_headers()

    conn.request("POST", "/jira/rest/api/2/search", json.dumps(payload), headers)

    res = conn.getresponse()
    data = res.read()

    # Filter Jira tickets ...
    issues = json.loads(data)['issues']
    if len(issues) != 1:
        raise ValueError("Invalid Ticket Number Size")

    return list(map(lambda x: x["key"], issues))[0]


def fetch_ticket_info(id):
    conn = http.client.HTTPSConnection("www.mulesoft.org")
    headers = build_headers()
    conn.request("GET", "/jira/rest/api/2/issue/" + id, headers=headers)
    res = conn.getresponse()
    data = res.read()

    return json.loads(data)


def fetch_subtask_from_id(id):
    ticket_info = fetch_ticket_info(id)

    subtasksIds = ticket_info['fields']["subtasks"]
    return list(map(lambda x: x["key"], subtasksIds))


def fetch_artifact_from_info(sid):
    ticket_info = fetch_ticket_info(sid)
    artifact_id = ticket_info["fields"]["components"][0]["name"]
    artifact_version = ticket_info["fields"]["versions"][0]["name"]
    return {"id": artifact_id, "version": artifact_version}


def fetch_artifacts():
    # Fetch all the events ...
    storiesKey = fetch_tickets_ready_to_deploy()

    # Fetch the first ticket to be deployed ...
    subtasksIds = fetch_subtask_from_id(storiesKey)

    # Fetch artifact Version ...
    return list(map(lambda x: fetch_artifact_from_info(x), subtasksIds))


print(fetch_artifacts())

