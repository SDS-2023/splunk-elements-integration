class ActionResult(object):
    def update_summary(self, arg):
        return {
                "num_data": 0
                }
    def get_data(self):
        return '{ "name":"event1" }'
    def set_status(self, arg):
        return 1
    def get_status(self):
        return 0
    def add_data(self, arg):
        return 0

class Connector(object):
    def __init__(self, config_connector):
        self._timestamp = config_connector["timestamp"]
        self._state = config_connector["state"]	
        self._client_id = config_connector["client_id"]
        self._client_secret = config_connector["client_secret"]
        self._base_url = config_connector["base_url"]
        self.response = config_connector["response"]
    def save_container(self, container, fail_on_duplicate):
        return 0,"Message",0
    def get_container_info(self, container_id):
        return [False, True]
    def save_artifacts(self, artifacts):
        return 1, "Message", 2 
    def save_progress(self, arg):
        return
    def get_action_identifier(self):
        return
    def add_action_result(self, arg):
        action_result = ActionResult()
        return action_result
    def _make_rest_call(self, endpoint, action_result, method="get", **kwargs):
        return 0, self.response
    def debug_print(self, message, val):
        return