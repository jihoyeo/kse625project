import os
from os.path import join
import json

class JSONLoader:
    
    def __init__(self, json_file, dir_data, fields = None, encoding = 'utf-8'):
        self.home = os.path.expanduser('~')
        self.dir_data = join(self.home, dir_data)
        self.dir_json = join(self.dir_data, json_file)
        self.fields = self.init_fields(fields)
        self.condition = dict()
        self.encoding = encoding
        
    def set_condition(self, **kwargs):
        for key, value in kwargs.items():
            self.condition[key] = set(value)
    
    def init_fields(self, fields):
        with open(self.dir_json) as f:
            for i, line in enumerate(f):
                # read only the first line
                if i > 1:
                    break
                json_line = json.loads(line)
                if fields == None:
                    fields = [key for key, value in json_line.items()]
                else:
                    fields = [key for key, value in json_line.items() if key in fields]
        return fields
    
    def sample(self, n_samples):
        
        data = []
        fields = set(self.fields)

        f = open(self.dir_json, encoding = self.encoding)

        for i, line in enumerate(f):
            if i >= n_samples:
                break
            json_line = json.loads(line)
            data.append([])
            
            valid_items = [(key, value) for (key, value) in json_line.items()
                           if key in fields or key in self.condition]
            
            for key, value in valid_items:
                # value should be a list
                value_list = []
                if not type(value) == list:
                    value_list = [value]
                else:
                    value_list = value
                if key in self.condition:
                    if len(set(value_list) & self.condition[key]) <= 0:
                        del data[-1] # do not add this line
                        break
                    if key not in fields:
                        continue
                data[-1].append(value)

        f.close()
#         print(n_valid)
        
        return self.fields, data