class History:  # Tracks data for requests and logs the user queries

    def __init__(self, log_dict):
        self.log = log_dict    # Contains user query logs based on telegram id
        self.data = dict()     # Contains temporary personal request data


history = History(log_dict=dict())