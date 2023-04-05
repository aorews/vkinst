import json
import os


class BaseConfig:
    def __init__(self, path):
        self.path = path
        self.config = self.read_config()

    def read_config(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                data = json.load(f)
            return data
        else:
            return dict()

    def write_config(self):
        with open(self.path, "w") as f:
            json.dump(self.config, f)
