class ActionResult(object):
    def __init__(self, *args, **kwargs):
        pass
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