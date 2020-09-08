# -*- coding:utf-8 -*-
import time
import copy
import requests
import hashlib
import re

#API_URL
MAIN_URL = "http://125.35.5.51/cap-aco-bx"
SIGN_HS_URL = "http://125.35.5.51/cap-aco-bx/signInController/findSignInInfoByCondition"
LOGIN_URL = "http://125.35.5.51/cap-aco-bx/login"

#这两个参数用来请求数据用
ZS_DATE_START = time.strftime('%Y-%m-%d',time.localtime())+' 00:00:00'
ZS_DATE_END = time.strftime('%Y-%m-%d',time.localtime())+' 09:30:00'
WS_DATE_START = time.strftime('%Y-%m-%d',time.localtime())+' 18:00:00'
WS_DATE_END = time.strftime('%Y-%m-%d',time.localtime())+' 23:59:59'

# app = Flask(__name__)


HEADERS = {
    'Host':'125.35.5.51',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
}

COOKIE = "Cookie"
EMPTY_STR = r''
ROWS = 'rows'
EQUAL = r'='
# COOKIE_VAL = "sid=b83ff1ce-517a-491f-a342-c2e0a9327de1; username=yz; password=; rememberme=0; autoSubmit=0; sys=OA"
N_COOKIE = {
    'sid':'b83ff1ce-517a-491f-a342-c2e0a9327de1',
    'username':'yz',
    'password':'',
    'rememberme':'0',
    'autoSubmit':'0',
    'sys':'OA'
}
LOGIN_PARAM = {
    'sys':'OA',
    'username':'yz',
    'password':'yy616499',
    'rememberme':'0',
    'autoSubmit':'0'
}

s = requests.Session()

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
        result = s.get(url=SIGN_HS_URL, cookies=N_COOKIE, params=SIGN_HS_DATE, headers=HEADERS,  timeout=5)
        print('result结果是')
        print(result)
        url = str(result.url)
        print('url是'+url)
        if bool(re.search('cap-aco-bx/login',url)) == False:
            returnData = result.json()
            if returnData['rows'] != []:
                #获取数据库取到的打卡时间
                #datats = int(time.mktime(time.strptime(i['signInDate'][:19], "%Y-%m-%d %H:%M:%S")))
                print('打过卡了，真棒！')
                push_wechat("已经打过卡了，真棒！", "这是今天的打卡情况："+returnData['rows'][0]['signInDate']+"")
                return '打过卡了，真棒！'
            else:
                print('该打卡了')
                push_wechat("打卡时间到了！", "今天还没打卡，快去打卡吧！")
                return '该打卡了'
        else:
            print('cookie过期了')
            push_wechat("cookie过期了！", "cookie过期了，请重新设置！")
            return  'cookie过期了'
    except Exception as e:
        print('异常了')
        push_wechat("程序异常了，请检查！", "程序异常了，请检查！")
        return '异常了'

def chuli_date(type, ts, startjz):
    if type == 'z':
        if ts > startjz:
            return False
def push_wechat(title, desp):
    requests.get(url="https://sc.ftqq.com/SCU112622Td6ab1713c2c49f53019938b14b42c8055f564265d31e7.send?text="+title+"&desp="+desp+"当前时间是："+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"",  timeout=5)

# @app.route('/getStatus', methods=['GET'])
def main():
    #这几个时间ts用来做判断用
    TS_DATE_START_JZ = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 09:30:00', "%Y-%m-%d %H:%M:%S")))
    TS_DATE_END_START = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 18:30:00', "%Y-%m-%d %H:%M:%S")))
    TS_DATE_END_JZ = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 20:00:00', "%Y-%m-%d %H:%M:%S")))
    #判断当前时间来决定提醒早上打卡还是晚上打卡
    print('开始判断当前时间属于早上打卡还是晚上打卡')
    nowts = int(time.time())
    res = ""
    if nowts < TS_DATE_START_JZ:
        print('现在是早上打卡时间')
        res = get_sign_hs(ZS_DATE_START, ZS_DATE_END)
    if nowts > TS_DATE_END_START:
        print('现在是晚上上打卡时间')
        res = get_sign_hs(WS_DATE_START, WS_DATE_END)
    else:
        print('计划时间外！')
        res = "还没到时间"
    return res

def getCookie():
    result = s.post(LOGIN_URL, LOGIN_PARAM)
    N_COOKIE['sid'] = result.request.headers['Cookie'].split(';')[0].split('=')[1]

if __name__ == '__main__':
    # app.run()
    getCookie()
    main()
