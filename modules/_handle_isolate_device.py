import phantom.app as phantom
from phantom.action_result import ActionResult

from modules._get_token import _get_token

def _handle_isolate_device(self, param):
    self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))
    # Add an action result object to self (BaseConnector) to represent the action for this param
    action_result = self.add_action_result(ActionResult(dict(param)))

    devices = [param['device_id']]
    client_id = self._client_id
    client_secret = self._client_secret
    base_url = self._base_url
    token = _get_token(client_id, client_secret, base_url)
    headers = {'Authorization': f'Bearer ' + token}
    ret_val, response = self._make_rest_call(
        'whoami/v1/whoami', action_result, params=None, headers=headers
    )
    organizationId = response["organizationId"]
    params = {"organizationId": organizationId, "deviceId": param['device_id']}
    ret_val, response = self._make_rest_call(
        "devices/v1/operations", action_result, params=params, headers=headers
    )
    operations = response['items']
    ret_val, response = self._make_rest_call(
        "devices/v1/devices", action_result, params=params, headers=headers
    )
    state = response['items'][0]['state']
    print(state)
    isolated = False
    isolate_queued = False
    for i in operations:
        if i['operationName'] == 'isolateFromNetwork' and i['status'] == 'pending':
            isolate_queued = True
            continue

    if state != 'isolated' and isolate_queued == False:
        headers = {"Content-Type": "application/json", 'Authorization': f'Bearer {token}'}
        data = {"operation": "isolateFromNetwork",
                "parameters": {"message": "Your device will be isolated"}, "targets": devices}
        ret_val, response = self._make_rest_call(
            'devices/v1/operations', action_result, json=data, headers=headers, method="post")

        if response.get('multistatus') is not None:
            for i in response['multistatus']:
                if i["status"] == 202:
                    print("Device: ", i["target"], "SUCCESSFULLY ISOLATED")
                    isolated = True
                else:
                    print("Device: ", i["target"], "ERROR OCCURRED")
        else:
            print('Token Request Failed:', response.text)
    else:
        print("Device is alredy isolated, or isolating is queued")
    if phantom.is_fail(ret_val):
        # the call to the 3rd party device or service failed, action result should contain all the error details
        # for now the return is commented out, but after implementation, return from here
        return action_result.get_status()
        pass
    # Add a dictionary that is made up of the most important values from data into the summary
    summary = action_result.update_summary({'Completed': True, 'isolated': isolated})
    summary['num_data'] = len(action_result.get_data())

    # Return success, no need to set the message, only the status
    # BaseConnector will create a textual message based off of the summary dictionary
    return action_result.set_status(phantom.APP_SUCCESS)