# -*- coding:utf-8 -*-
import time
import copy
import requests
import hashlib
import re
from flask import Flask
from flask import request

#API_URL
MAIN_URL = "http://125.35.5.51/cap-aco-bx"
SIGN_HS_URL = "http://125.35.5.51/cap-aco-bx/signInController/findSignInInfoByCondition"

#这两个参数用来请求数据用
ZS_DATE_START = time.strftime('%Y-%m-%d',time.localtime())+' 00:00:00'
ZS_DATE_END = time.strftime('%Y-%m-%d',time.localtime())+' 09:30:00'
WS_DATE_START = time.strftime('%Y-%m-%d',time.localtime())+' 18:00:00'
WS_DATE_END = time.strftime('%Y-%m-%d',time.localtime())+' 23:59:59'

app = Flask(__name__)


HEADERS = {
    'Host':'125.35.5.51',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
}

COOKIE = "Cookie"
EMPTY_STR = r''
ROWS = 'rows'
EQUAL = r'='
COOKIE_VAL = "sid=a509e711-2acd-4e58-a3dc-853e8994b036; username=yz; password=; rememberme=0; autoSubmit=0; sys=OA"
N_COOKIE = {
    'sid':'93e2f706-d053-42f9-a093-e968fb87ce12',
    'username':'yz',
    'password':'',
    'rememberme':'0',
    'autoSubmit':'0',
    'sys':'OA'
}

def get_sign_hs(start, end):
    # headers = copy.copy(HEADERS)
    # headers.update({COOKIE: EMPTY_STR.join([COOKIE, cd])})
    SIGN_HS_DATE = {
        'pageNum':'0',
        'pageSize':'5',
        'queryUserName':'杨哲',
        'queryTools':'2',
        'queryStartTime':start,
        'queryEndTime':end
    }
    try:
        result = requests.get(url=SIGN_HS_URL, cookies=N_COOKIE, params=SIGN_HS_DATE, headers=HEADERS,  timeout=5)
        url = str(result.url)
        if bool(re.search('cap-aco-bx/login',url)) == False:
            returnData = result.json()
            if returnData['rows'] != []:
                #获取数据库取到的打卡时间
                #datats = int(time.mktime(time.strptime(i['signInDate'][:19], "%Y-%m-%d %H:%M:%S")))
                print('打过卡了，真棒！')
                return '打过卡了，真棒！'
            else:
                print('该打卡了')
                return '该打卡了'
        else:
            print('cookie过期了')
            return  'cookie过期了'
    except Exception as e:
        print('异常了')
        return '异常了'

def chuli_date(type, ts, startjz):
    if type == 'z':
        if ts > startjz:
            return False

@app.route('/getStatus', methods=['GET'])
def main():
    #这几个时间ts用来做判断用
    TS_DATE_START_JZ = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 09:30:00', "%Y-%m-%d %H:%M:%S")))
    TS_DATE_END_START = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 18:30:00', "%Y-%m-%d %H:%M:%S")))
    TS_DATE_END_JZ = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 20:00:00', "%Y-%m-%d %H:%M:%S")))
    #判断当前时间来决定提醒早上打卡还是晚上打卡
    nowts = int(time.time())
    res = ""
    if nowts < TS_DATE_START_JZ:
        res = get_sign_hs(ZS_DATE_START, ZS_DATE_END)
    if nowts > TS_DATE_END_START:
        res = get_sign_hs(WS_DATE_START, WS_DATE_END)
    else:
        print('还没到时间')
        res = "还没到时间"
    return res

if __name__ == '__main__':
    app.run()