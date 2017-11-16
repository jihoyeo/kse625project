import os
from os.path import join
import json

class JSONLoader:
    
    def __init__(self, json_file, dir_data, fields = None):
        self.home = os.path.expanduser('~')
        self.dir_data = join(self.home, dir_data)
        self.dir_json = join(self.dir_data, json_file)
        self.fields = fields
        
    def sample(self, n_samples):
        if not self.fields == None:
            fields = set(self.fields)
            data = []
            with open(self.dir_json) as f:
                for i, line in enumerate(f):
                    if i >= n_samples:
                        break
                    json_line = json.loads(line)
                    data.append([])
                    for key, value in json_line.items():
                        if key in fields:
                            data[-1].append(value)
        else:
            data = []
            with open(self.dir_json) as f:
                for i, line in enumerate(f):
                    if i >= n_samples:
                        self.fields = list(json_line.keys())
                        break
                    json_line = json.loads(line)
                    data.append([])
                    for key, value in json_line.items():
                        data[-1].append(value)
        return self.fields, data