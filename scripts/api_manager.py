import os
import json

class ApiManager:
    STATE_FILE = ".api_state.json"

    def __init__(self, keys):
        self.keys = keys
        # load last index or start at 0
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, "r") as f:
                state = json.load(f)
                self.index = state.get("index", 0)
        else:
            self.index = 0

    def get_next_key(self):
        key = self.keys[self.index % len(self.keys)]
        self.index = (self.index + 1) % len(self.keys)
        # save state
        with open(self.STATE_FILE, "w") as f:
            json.dump({"index": self.index}, f)
        return key
