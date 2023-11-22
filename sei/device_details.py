import phantom.app as phantom

def device_details(connector, action_result, param):
    connector.save_progress("In action handler for: {0}".format(connector.get_action_identifier()))

    client_id = connector._client_id
    client_secret = connector._client_secret

    data = {"grant_type": "client_credentials", "scope": "connect.api.read connect.api.write"}
    ret_val, response = connector._make_rest_call("as/token.oauth2", action_result, data=data, headers=None, method="post", auth=(client_id, client_secret))
    token = response['access_token']

    headers = {'Authorization': f'Bearer ' + token}
    ret_val, response = connector._make_rest_call(
        'whoami/v1/whoami', action_result, params=None, headers=headers
    )
    organizationId = response["organizationId"]
    params = {"organizationId": organizationId, "deviceId": param['device_id']}
    ret_val, response = connector._make_rest_call(
        "devices/v1/operations", action_result, params=params, headers=headers
    )
    isolate_queued = False
    if response is not None:
        operations = response['items']
        
        for i in operations:
            if i['operationName'] == 'isolateFromNetwork' and i['status'] == 'pending':
                isolate_queued = True

    ret_val, response = connector._make_rest_call(
        "devices/v1/devices", action_result, params=params, headers=headers
    )
    device_info = {}
    device = {}
    if response is not None:
        device = response['items'][0]

    device_info["isolate_queued"] = isolate_queued
    device_info.update(device)
    
    action_result.add_data(device_info)

    if phantom.is_fail(ret_val):
        return action_result.get_status()

    summary = action_result.update_summary({'Completed': True})

    return action_result.set_status(phantom.APP_SUCCESS)