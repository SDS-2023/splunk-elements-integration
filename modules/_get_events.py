from phantom.action_result import ActionResult
from modules._get_token import _get_token

def _get_events(self, param):
    self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))
    # Add an action result object to self (BaseConnector) to represent the action for this param
    action_result = self.add_action_result(ActionResult(dict(param)))
    client_id = self._client_id
    client_secret = self._client_secret
    base_url = self._base_url
    containerId = self._container_id
    if self.get_container_info(containerId)[0] == True:
        timestamp = self.get_container_info(containerId)[1]['tags'][0]
        containerCount = self.get_container_info(containerId)[1]['artifact_count'] + 1
    else:
        containerCount = 1
        timestamp = '2022-08-01T00:00:01Z'
        #2023-09-15T00:00:01Z
        #2022-08-01T00:00:01Z

    token = _get_token(client_id, client_secret, base_url)
    print(token)
    headers = {'Authorization': f'Bearer ' + token}
    ret_val, response = self._make_rest_call(
        'whoami/v1/whoami', action_result, params=None, headers=headers
    )
    organizationId = response["organizationId"]
    events = None
    params = {"organizationId": organizationId, "engine": "",
              "persistenceTimestampStart": timestamp}
    ret_val, response = self._make_rest_call(
        "security-events/v1/security-events", action_result, params=params, headers=headers
    )

    if response.get("items") is not None:
        events = response.get("items")
        while response.get("nextAnchor") is not None:
            params["anchor"] = response.get("nextAnchor")
            ret_val, response = self._make_rest_call(
                "security-events/v1/security-events", action_result, params=params, headers=headers
            )
            events.extend(response.get("items"))

    artifacts = []

    if events is not None:
        if len(events) > 0:
            new_timestamp = events[0]["persistenceTimestamp"]
            for i in events:
                severity = i['severity']
                artifact = {"name": 'Event ' + str(containerCount), "label": severity, "severity": severity,
                            'artifact_type': 'event', "data": i, "cef": i, "container_id": containerId}
                artifacts.append(artifact)
                containerCount += 1
    return artifacts, new_timestamp, action_result