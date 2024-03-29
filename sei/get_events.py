def get_events(connector, action_result, containerId, timestamp):
    connector.save_progress("In action handler for: {0}".format(connector.get_action_identifier()))
    client_id = connector._client_id
    client_secret = connector._client_secret
    new_timestamp = timestamp
    
    data = {"grant_type": "client_credentials", "scope": "connect.api.read connect.api.write"}
    ret_val, response = connector._make_rest_call("as/token.oauth2", action_result, data=data, headers=None, method="post", auth=(client_id, client_secret))
    token = response['access_token']
    print(token)

    headers = {'Authorization': f'Bearer ' + token}
    ret_val, response = connector._make_rest_call(
        'whoami/v1/whoami', action_result, params=None, headers=headers
    )
    organizationId = response["organizationId"]
    events = None

    headers = {'Authorization': f'Bearer {token}', "Accept": "application/json"}

    params = {"organizationId": organizationId, "engineGroup": ["edr", "epp", "ecp"], "persistenceTimestampStart": timestamp, "exclusiveStart": True}

    ret_val, response = connector._make_rest_call(
        "security-events/v1/security-events", action_result, data=params, headers=headers, method="post"
    )

    artifacts = []
    if response is not None:
        
        if response.get("items") is not None:
            events = response.get("items")
            while response.get("nextAnchor") is not None:
                if events is not None:
                    if len(events) > 0:
                        new_timestamp = events[0]["persistenceTimestamp"]
                        for i in events:
                            severity = i['severity']
                            artifact = {"name": i['id'], "label": severity, "severity": severity,
                                        'artifact_type': 'event', "data": i, "cef": i, "container_id": containerId, 'run_automation': True}
                            artifacts.append(artifact)
                    if len(artifacts) >= 2000:
                        success, message, id_list = connector.save_artifacts(artifacts)
                        artifacts = []
                params["anchor"] = response.get("nextAnchor")
                ret_val, response = connector._make_rest_call(
                    "security-events/v1/security-events", action_result, data=params, headers=headers, method="post"
                )
                events = response.get("items")

            if events is not None:
                connector.debug_print("Number of loaded events", len(events))
                if len(events) > 0:
                    new_timestamp = events[0]["persistenceTimestamp"]
                    for i in events:
                        severity = i['severity']
                        artifact = {"name": i['id'], "label": severity, "severity": severity,
                                    'artifact_type': 'event', "data": i, "cef": i, "container_id": containerId, 'run_automation': True}
                        artifacts.append(artifact)
                success, message, id_list = connector.save_artifacts(artifacts)

    return artifacts, new_timestamp, action_result