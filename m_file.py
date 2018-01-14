"""
file module - handles file operations
mainly ini/json file storage of dictionaries
"""
from os import getcwd, path #import os
import json

class ini:
    """
    class for ini file operations
    """
    def __init__(self):
        self.version = '0.1'
        self.host = ''
        self.port = 0
    def read(self, file1):
        """
        reads ini file, returns dictionary
        """
        dir_path = path.dirname(path.realpath(__file__))
        print(dir_path)
        with open(path.join(dir_path, file1)) as data_file:
            data_loaded = json.load(data_file)
        return data_loaded
    def write(self, file1, data):
        """
        writes dictionary into the file
        """
        pass