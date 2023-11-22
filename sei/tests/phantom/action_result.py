class ActionResult(object):
    def __init__(self, *args, **kwargs):
        self.data = []
        self.status = None
        self.summary = {}

    def update_summary(self, arg):
        self.summary.update(arg)
        return self.summary

    def add_data(self, arg):
        self.data.append(arg)

    def get_data(self):
        return self.data
    
    def set_status(self, arg):
        return 1
    
    def get_status(self):
        return 0
