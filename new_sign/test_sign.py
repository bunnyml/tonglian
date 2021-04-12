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

def signIn():
    time.strftime('%Y-%m-%d',time.localtime())+' 21:30:00'
    result = s.get(url=MAIN_URL+USER_SIGN_URL, cookies=N_COOKIE, params=PARAME_DATA, headers=HEADERS)
    text = result.json()
    if text['result'] == 0:
        logger.info("打卡成功")
        push_wechat()

def __init__(self,Id,Token):
    get_new_ip(self)
    self.login_token=str(Id)+","+str(Token)
    self.format="xml"
    self.lang="cn"
    self.headers={"User-Agent":"ddns_for_raspberry_pi/0.1(heeeepin@gmail.com)"}
    self.api='https://dnsapi.cn/'
    self.ip='http://members.3322.org/dyndns/getip'
    self.data={"login_token":self.login_token,"format":self.format,"lang":self.lang}
    self.path=os.path.dirname(os.path.realpath(__file__))
    self.domain_list=self.load()
