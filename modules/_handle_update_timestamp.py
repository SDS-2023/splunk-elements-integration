import phantom.app as phantom

from modules._get_events import _get_events

def _handle_update_timestamp(self, param):
    artifacts, new_timestamp, action_result = _get_events(self, param)
    
    # Add a dictionary that is made up of the most important values from data into the summary
    summary = action_result.update_summary({'Completed': True})
    summary['num_data'] = len(artifacts)
    summary['timestamp'] = new_timestamp
    print(new_timestamp)
    # Return success, no need to set the message, only the status
    # BaseConnector will create a textual message based off of the summary dictionary
    return action_result.set_status(phantom.APP_SUCCESS)
    
    # For now return Error with a message, in case of success we don't set the message, but use the summary
    return action_result.set_status(phantom.APP_ERROR, "Action not yet implemented")