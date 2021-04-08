# -*- coding:utf-8 -*-

import json
import time
import os
import requests

def load(self):
    file=self.path+'/config.json'
    with open(file,'r') as f:
        data=json.load(f)
    return data

def get_new_ip(self):
    return requests.get(url=self.ip).text

def __init__(self,Id,Token):
    get_new_ip(self)
    