import phantom.app as phantom

from modules._get_events import _get_events

def _handle_on_poll(self, param):
    if self.get_container_info(self._container_id)[0] == False:
        artifacts, new_timestamp, action_result = _get_events(self, param)

        container = {'name': 'WithSecure - security events', 'label': 'events',
                     'container_type': 'default', 'artifacts': artifacts, 'tags': [new_timestamp]}
        success, message, container_id = self.save_container(container)
        print(success, "M: ", message)
        # Add the response into the data section
        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({'Completed': True})
        summary['num_data'] = len(action_result.get_data())

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    else:
        artifacts, new_timestamp, action_result = _get_events(self, param)

        if len(artifacts) > 0:
            success, message, id_list = self.save_artifacts(artifacts)
            action_result.add_extra_data({'timestamp': new_timestamp})
        else:
            action_result.add_extra_data({'timestamp': timestamp})
        # Add the response into the data section

        # Add a dictionary that is made up of the most important values from data into the summary
        summary = action_result.update_summary({'Completed': True})
        summary['num_data'] = len(action_result.get_data())

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)