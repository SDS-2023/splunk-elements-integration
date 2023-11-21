import phantom.app as phantom

def isolate_device(connector, action_result, param):
    connector.save_progress("In action handler for: {0}".format(connector.get_action_identifier()))
    isolated = False
    devices = [param['device_id']]
    if devices[0] not in connector._state["isolated_devices"]:

        connector._state["isolated_devices"] = connector._state["isolated_devices"] + devices 
        client_id = connector._client_id
        client_secret = connector._client_secret

        data = {"grant_type": "client_credentials", "scope": "connect.api.read connect.api.write"}
        ret_val, response = connector._make_rest_call("as/token.oauth2", action_result, data=data, headers=None, method="post", auth=(client_id, client_secret))
        token = response['access_token']

        headers = {"Content-Type": "application/json", 'Authorization': f'Bearer {token}'}
        data = {"operation": "isolateFromNetwork",
                "parameters": {"message": "Your device will be isolated"}, "targets": devices}
        ret_val, response = connector._make_rest_call(
            'devices/v1/operations', action_result, json=data, headers=headers, method="post")

        if response is not None:
            for i in response['multistatus']:
                if i["status"] == 202:
                    print("Device: ", i["target"], "SUCCESSFULLY ISOLATED")
                    isolated = True
                else:
                    print("Device: ", i["target"], "ERROR OCCURRED")
        else:
            print('Token Request Failed')

        if phantom.is_fail(ret_val):
            return action_result.get_status()

    summary = action_result.update_summary({'completed': True, 'isolated': isolated})

    return action_result.set_status(phantom.APP_SUCCESS)