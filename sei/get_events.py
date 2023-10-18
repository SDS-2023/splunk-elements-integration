from phantom.action_result import ActionResult
from .get_token import get_token

def get_events(connector, param, containerId, timestamp):
    connector.save_progress("In action handler for: {0}".format(connector.get_action_identifier()))
    action_result = connector.add_action_result(ActionResult(dict(param)))
    client_id = connector._client_id
    client_secret = connector._client_secret
    base_url = connector._base_url

    token = get_token(client_id, client_secret, base_url)
    print(token)
    headers = {'Authorization': f'Bearer ' + token}
    ret_val, response = connector._make_rest_call(
        'whoami/v1/whoami', action_result, params=None, headers=headers
    )
    organizationId = response["organizationId"]
    events = None


    params = {"organizationId": organizationId, "engine": "", "persistenceTimestampStart" : timestamp}

    ret_val, response = connector._make_rest_call(
        "security-events/v1/security-events", action_result, params=params, headers=headers
    )

    if response.get("items") is not None:
        events = response.get("items")
        while response.get("nextAnchor") is not None:
            params["anchor"] = response.get("nextAnchor")
            ret_val, response = connector._make_rest_call(
                "security-events/v1/security-events", action_result, params=params, headers=headers
            )
            events.extend(response.get("items"))

    artifacts = []

    if events is not None:
        connector.debug_print("Number of loaded events", len(events))
        if len(events) > 0:
            new_timestamp =  events[0]["persistenceTimestamp"]
            for i in events:
                severity = i['severity']
                artifact = {"name": i['id'], "label": severity, "severity": severity,
                            'artifact_type': 'event', "data": i, "cef": i, "container_id": containerId}
                artifacts.append(artifact)
    return artifacts, new_timestamp, action_result