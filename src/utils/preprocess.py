import os
from os.path import join
import json

import os
from os.path import join
import json

class JSONLoader:
    
    def __init__(self, json_file, dir_data, fields = None):
        self.home = os.path.expanduser('~')
        self.dir_data = join(self.home, dir_data)
        self.dir_json = join(self.dir_data, json_file)
        self.fields = fields
        self.condition = dict()
        
    def set_condition(self, **kwargs):
        for key, value in kwargs.items():
            self.condition[key] = set(value)
        
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
                            valid_key = key not in self.condition or\
                            key in self.condition and len(set(value) & self.condition[key]) > 0
                            if not valid_key:
                                del data[-1] # do not add this line
                                break
                            else:
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
                        valid_key = key not in self.condition or\
                        key in self.condition and len(set(value) & self.condition[key]) > 0
                        if not valid_key:
                            del data[-1] # do not add this line
                            break
                        else:
                            data[-1].append(value)
        return self.fields, data