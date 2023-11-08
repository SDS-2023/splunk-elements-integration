import phantom.app as phantom

import sei

def on_poll(connector, param):
    timestamp = connector._timestamp if connector._timestamp != None else connector._state["last_poll"] if "last_poll" in connector._state.keys()  else '2022-08-01T00:00:01Z'
    container_id = connector._state["container_id"] if "container_id" in connector._state.keys() else None
    print(timestamp)
    if container_id is None or connector.get_container_info(container_id)[0] == False:
        container = {'name': 'WithSecure - security events', 'label': 'events',
                     'container_type': 'default', "run_automation": True}
        success, message, container_id = connector.save_container(container, fail_on_duplicate=True)


    artifacts, new_timestamp, action_result = sei.get_events(connector, param, container_id, timestamp)
    if len(artifacts) > 0:
            success, message, id_list = connector.save_artifacts(artifacts)

    connector._state["isolated_devices"] = []
    connector._state["last_poll"] = new_timestamp
    connector._state["container_id"] = container_id
    summary = action_result.update_summary({'Completed': True})
    summary['num_data'] = len(action_result.get_data())

    return action_result.set_status(phantom.APP_SUCCESS)