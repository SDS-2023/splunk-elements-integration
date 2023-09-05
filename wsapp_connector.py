#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------
# Phantom sample App Connector python file
# -----------------------------------------

# Python 3 Compatibility imports
from __future__ import print_function, unicode_literals

# Phantom App imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult
import phantom.rules as ph

# Usage of the consts file is recommended
# from wsapp_consts import *
import requests
import json
from bs4 import BeautifulSoup
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from datetime import datetime, timezone, timedelta

class RetVal(tuple):

    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class WsAppConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(WsAppConnector, self).__init__()

        self._state = None

        # Variable to hold a base_url in case the app makes REST calls
        # Do note that the app json defines the asset config, so please
        # modify this as you deem fit.
        self._base_url = None
        self._client_id = None
        self._client_secret = None

    def _process_empty_response(self, response, action_result):
        if response.status_code == 200:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(
            action_result.set_status(
                phantom.APP_ERROR, "Empty response and no information in the header"
            ), None
        )

    def _process_html_response(self, response, action_result):
        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split('\n')
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = '\n'.join(split_lines)
        except:
            error_text = "Cannot parse error details"

        message = "Status Code: {0}. Data from server:\n{1}\n".format(status_code, error_text)

        message = message.replace(u'{', '{{').replace(u'}', '}}')
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR, "Unable to parse JSON response. Error: {0}".format(str(e))
                ), None
            )

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        # You should process the error returned in the json
        message = "Error from server. Status Code: {0} Data from server: {1}".format(
            r.status_code,
            r.text.replace(u'{', '{{').replace(u'}', '}}')
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r, action_result):
        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, 'add_debug_data'):
            action_result.add_debug_data({'r_status_code': r.status_code})
            action_result.add_debug_data({'r_text': r.text})
            action_result.add_debug_data({'r_headers': r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if 'json' in r.headers.get('Content-Type', ''):
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if 'html' in r.headers.get('Content-Type', ''):
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {0} Data from server: {1}".format(
            r.status_code,
            r.text.replace('{', '{{').replace('}', '}}')
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _get_token(self, client_id, client_secret, base_url):
        token_url = base_url + 'as/token.oauth2'
        data = {
            "grant_type": "client_credentials",
            "scope": "connect.api.read connect.api.write",
        }
        response = requests.post(token_url, auth=(client_id, client_secret), data=data)
        token_json = response.json()
        token = token_json.get("access_token")
        return token

    def _make_rest_call(self, endpoint, action_result, method="get", **kwargs):
        # **kwargs can be any additional parameters that requests.request accepts

        config = self.get_config()

        kwargs['headers'] = kwargs.get("headers")
        kwargs['params'] = kwargs.get("params")
        kwargs['json'] = kwargs.get("json")
        resp_json = None

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return RetVal(
                action_result.set_status(phantom.APP_ERROR, "Invalid method: {0}".format(method)),
                resp_json
            )

        # Create a URL to connect to
        url = self._base_url + endpoint

        try:
            r = request_func(
                url,
                # auth=(username, password),  # basic authentication
                verify=config.get('verify_server_cert', False),
                **kwargs
            )
        except Exception as e:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR, "Error Connecting to server. Details: {0}".format(str(e))
                ), resp_json
            )
        
        return self._process_json_response(r, action_result)

    def _handle_test_connectivity(self, param):
        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # NOTE: test connectivity does _NOT_ take any parameters
        # i.e. the param dictionary passed to this handler will be empty.
        # Also typically it does not add any data into an action_result either.
        # The status and progress messages are more important.

        self.save_progress("Connecting to endpoint")
        # make rest call
        ret_val, response = self._make_rest_call(
            'whoami/v1/whoami', action_result, params=None, headers=None
        )

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            # for now the return is commented out, but after implementation, return from here
            self.save_progress("Test Connectivity Failed.")
            # return action_result.get_status()

        # Return success
        self.save_progress("Test Connectivity Passed")
        return action_result.set_status(phantom.APP_SUCCESS)

        # For now return Error with a message, in case of success we don't set the message, but use the summary
        return action_result.set_status(phantom.APP_ERROR, "Action not yet implemented")

    def _handle_get_events(self, param):
        # Implement the handler here
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary

        # Required values can be accessed directly
        # required_parameter = param['required_parameter']

        # Optional values should use the .get() function

        # make rest call
        client_id = self._client_id
        client_secret = self._client_secret
        base_url = self._base_url
        token = self._get_token(client_id, client_secret, base_url)
        headers = {'Authorization': f'Bearer ' + token}
        ret_val, response = self._make_rest_call(
            'whoami/v1/whoami', action_result, params=None, headers=headers
        )
        organizationId = response["organizationId"]
        params = {"organizationId": organizationId, "engine": "",
                  "persistenceTimestampStart": "2022-08-01T00:00:01Z"}
        ret_val, response = self._make_rest_call(
            "security-events/v1/security-events", action_result, params=params, headers=headers
        )
        if response.get("items") is not None :
            events = response.get("items")
            while response.get("nextAnchor") is not None:
                params["anchor"] = response.get("nextAnchor")
                ret_val, response = self._make_rest_call(
                    "security-events/v1/security-events", action_result, params=params, headers=headers
                    )
                events.extend(response.get("items"))
                
        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            # for now the return is commented out, but after implementation, return from here
            return action_result.get_status()
            pass
        # Now post process the data,  uncomment code as you deem fit
        artifacts = []
        k = 1
        if events is not None:
            for i in events:
                action_result.add_data(i)
                severity = i['severity']
                artifacts.append({"name": 'Event '+str(k),  "label": "event",  "severity": severity, 'artifact_type': 'event ', "data": i, "cef": i})
                k+=1
        container = {'containerId': 100, 'name': 'WithSecure - security events', 'label': 'events', 'container_type': 'default', 'artifacts': artifacts}
        success, message, container_id = self.save_container(container)
        print(success, "M: ", message)
        # Add the response into the data section
        
        print("Liczba Eventów: ", len(action_result.get_data()))
        print("Token: ", token)
        print("OrganizationId: ", organizationId)
        
        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({'Completed': True, 'organizationID': organizationId})
        summary['num_data'] = len(action_result.get_data())

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

        # For now return Error with a message, in case of success we don't set the message, but use the summary
        # return action_result.set_status(phantom.APP_ERROR, "Action not yet implemented")

    def _handle_poll_events(self, param):
        # Implement the handler here
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))
        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary

        # Required values can be accessed directly
        # required_parameter = param['required_parameter']

        # Optional values should use the .get() function

        # make rest call
        client_id = self._client_id
        client_secret = self._client_secret
        base_url = self._base_url
        token = self._get_token(client_id, client_secret, base_url)
        headers = {'Authorization': f'Bearer ' + token}
        ret_val, response = self._make_rest_call(
            'whoami/v1/whoami', action_result, params=None, headers=headers
        )
        organizationId = response["organizationId"]
        info = self.get_container_info(container_id=224)
        timestamp = datetime.strptime(info[1]['artifact_update_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        print(timestamp)
        params = {"organizationId": organizationId, "engine": "",
                  "persistenceTimestampStart": timestamp}
        ret_val, response = self._make_rest_call(
            "security-events/v1/security-events", action_result, params=params, headers=headers
        )
        if response.get("items") is not None :
            events = response.get("items")
            while response.get("nextAnchor") is not None:
                params["anchor"] = response.get("nextAnchor")
                ret_val, response = self._make_rest_call(
                    "security-events/v1/security-events", action_result, params=params, headers=headers
                    )
                events.extend(response.get("items"))
                
        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            # for now the return is commented out, but after implementation, return from here
            return action_result.get_status()
            pass
        # Now post process the data,  uncomment code as you deem fit
        artifacts = []
        k = 1
        container_id = self.get_container_id()
        if events is not None:
            for i in events:
                action_result.add_data(i)
                severity = i['severity']
                artifacts.append({"name": 'Event '+str(k),  "label": severity,  "severity": severity,
                                  'artifact_type': 'event ', "data": i, "cef": i, "container_id": 224, "run_automation": True, 'tags': 'new'})
                k+=1
        if len(artifacts) >=1:
            success, message, id_list = self.save_artifacts(artifacts)

        # Add the response into the data section
        
        print("Liczba Eventów: ", len(action_result.get_data()))
        print("Token: ", token)
        print("OrganizationId: ", organizationId)
        
        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({'Completed': True, 'organizationID': container_id})
        summary['num_data'] = len(action_result.get_data())

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

        # For now return Error with a message, in case of success we don't set the message, but use the summary
        # return action_result.set_status(phantom.APP_ERROR, "Action not yet implemented")

    def _handle_isolate_device(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))
        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))
        
        devices = [param['device_id']]
        client_id = self._client_id
        client_secret = self._client_secret
        base_url = self._base_url
        token = self._get_token(client_id, client_secret, base_url)
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

        # For now return Error with a message, in case of success we don't set the message, but use the summary
        # return action_result.set_status(phantom.APP_ERROR, "Action not yet implemented")

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS
        
        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == 'get_organizationid':
            ret_val = self._handle_get_organizationid(param)

        if action_id == 'get_events':
            ret_val = self._handle_get_events(param)

        if action_id == 'poll_events':
            ret_val = self._handle_poll_events(param)

        if action_id == 'isolate_device':
            ret_val = self._handle_isolate_device(param)

        if action_id == 'test_connectivity':
            ret_val = self._handle_test_connectivity(param)

        return ret_val

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        # get the asset config
        config = self.get_config()
        """
        # Access values in asset config by the name

        # Required values can be accessed directly
        required_config_name = config['required_config_name']

        # Optional values should use the .get() function
        optional_config_name = config.get('optional_config_name')
        """

        self._base_url = config.get('base_url')
        self._client_id = config.get('client_id')
        self._client_secret = config.get('client_secret')
        return phantom.APP_SUCCESS

    def finalize(self):
        # Save the state, this data is saved across actions and app upgrades
        self.save_state(self._state)
        return phantom.APP_SUCCESS


def main():
    import argparse

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input_test_json', help='Input Test JSON file')
    argparser.add_argument('-u', '--username', help='username', required=False)
    argparser.add_argument('-p', '--password', help='password', required=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password

    if username is not None and password is None:
        # User specified a username but not a password, so ask
        import getpass
        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = WsAppConnector._get_phantom_base_url() + '/login'

            print("Accessing the Login page")
            r = requests.get(login_url, verify=False)
            csrftoken = r.cookies['csrftoken']

            data = dict()
            data['username'] = username
            data['password'] = password
            data['csrfmiddlewaretoken'] = csrftoken

            headers = dict()
            headers['Cookie'] = 'csrftoken=' + csrftoken
            headers['Referer'] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=False, data=data, headers=headers)
            session_id = r2.cookies['sessionid']
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = WsAppConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json['user_session_token'] = session_id
            connector._set_csrf_info(csrftoken, headers['Referer'])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    exit(0)


if __name__ == '__main__':
    main()
