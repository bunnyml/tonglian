# -*- coding:utf-8 -*-
import time
import copy
import requests
import hashlib
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#API_URL
MAIN_URL = "http://125.35.5.51/cap-aco-bx"
SIGN_HS_URL = "http://125.35.5.51/cap-aco-bx/signInController/findSignInInfoByCondition"
LOGIN_URL = "http://125.35.5.51/cap-aco-bx/login"
PUSH_WECHAT = "https://sc.ftqq.com/SCU112622Td6ab1713c2c49f53019938b14b42c8055f564265d31e7.send"

#这两个参数用来请求数据用
ZS_DATE_START = time.strftime('%Y-%m-%d',time.localtime())+' 00:00:00'
ZS_DATE_END = time.strftime('%Y-%m-%d',time.localtime())+' 09:29:00'
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

SIGN_HS_DATE = {
    'pageNum':'0',
    'pageSize':'10',
    'queryUserName':'杨哲',
    'queryTools':'2',
    'queryStartTime':'',
    'queryEndTime':''
}

s = requests.Session()

def list_all_sign():
    logger.info("获取今天的打卡记录")
    SIGN_HS_DATE['queryStartTime'] = ZS_DATE_START
    SIGN_HS_DATE['queryEndTime'] = WS_DATE_END
    try:
        result = s.get(url=SIGN_HS_URL, cookies=N_COOKIE, params=SIGN_HS_DATE, headers=HEADERS,  timeout=5)
        url = str(result.url)
        if bool(re.search('cap-aco-bx/login',url)) == False:
            returnData = result.json()
            logger.info("这是获取到今天的打卡记录")
            logger.info(returnData['rows'])
            strs = ''
            strs += '姓名 | 打卡时间 | 打卡公司名称 | 打卡定位地点  \n'
            strs += '---------- | ---------- | ---------- | ---------- \n'
            for obj in returnData['rows']:
                strs += '【'+obj['userName']+'】 | 【'+obj['signInDate']+'】 | 【'+obj['localName']+'】 | 【'+obj['localAddress'] +'】'+ '\n'
            return strs
        else:
            push_wechat("cookie过期了！", "cookie过期了，请重新设置！")
            return "cookie过期"
    except Exception as e:
        push_wechat("程序异常了，请检查！", "程序异常了，请检查！")

def get_sign_hs(start, end):
    # headers = copy.copy(HEADERS)
    # headers.update({COOKIE: EMPTY_STR.join([COOKIE, cd])})
    logger.info("开始获取打卡记录")
    SIGN_HS_DATE['queryStartTime'] = start
    SIGN_HS_DATE['queryEndTime'] = end
    logger.info("拼接打卡记录参数完毕")
    try:
        logger.info("开始执行requests")
        result = s.get(url=SIGN_HS_URL, cookies=N_COOKIE, params=SIGN_HS_DATE, headers=HEADERS,  timeout=5)
        logger.info("执行requests完毕")
        url = str(result.url)
        logger.info("resut的url是"+url)
        if bool(re.search('cap-aco-bx/login',url)) == False:
            logger.info("判断url链接通过，开始判断是否该打卡了")
            returnData = result.json()
            if returnData['rows'] != []:
                logger.info("打过卡了")
                #获取数据库取到的打卡时间
                #datats = int(time.mktime(time.strptime(i['signInDate'][:19], "%Y-%m-%d %H:%M:%S")))
                signHistory = list_all_sign()
                # push_wechat("已经打过卡了，真棒！", "这是今天的打卡情况："+returnData['rows'][0]['signInDate']+"")
                push_wechat("已经打过卡了，真棒！", signHistory)
            else:
                logger.info("该打卡了")
                signHistory = list_all_sign()
                # push_wechat("打卡时间到了！", "今天还没打卡，快去打卡吧！"+signHistory)
                push_wechat("打卡时间到了！", signHistory)
        else:
            push_wechat("cookie过期了！", "cookie过期了，请重新设置！")
    except Exception as e:
        push_wechat("程序异常了，请检查！", "程序异常了，请检查！")

def chuli_date(type, ts, startjz):
    if type == 'z':
        if ts > startjz:
            return False
def push_wechat(title, desp):
    logger.info("开始执行微信推送")
    WECHAT_PARAM = {
        'text':title,
        'desp': desp + '\n\n\n\n > 查询时间：\n'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    # requests.get(url="https://sc.ftqq.com/SCU112622Td6ab1713c2c49f53019938b14b42c8055f564265d31e7.send?text="+title+"&desp="+desp+"当前时间是："+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"",  timeout=5)
    s.post(PUSH_WECHAT, WECHAT_PARAM)
    logger.info("微信推送执行完毕，结束运行")

# @app.route('/getStatus', methods=['GET'])
def main():
    logger.info("调用主方法")
    #这几个时间ts用来做判断用
    TS_DATE_START_JZ = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 09:30:00', "%Y-%m-%d %H:%M:%S")))
    TS_DATE_END_START = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 18:30:00', "%Y-%m-%d %H:%M:%S")))
    TS_DATE_END_JZ = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 20:00:00', "%Y-%m-%d %H:%M:%S")))
    #判断当前时间来决定提醒早上打卡还是晚上打卡
    logger.info("开始判断当前时间属于早上打卡还是晚上打卡")
    nowts = int(time.time())
    if nowts < TS_DATE_START_JZ:
        logger.info("现在是早上打卡时间")
        get_sign_hs(ZS_DATE_START, ZS_DATE_END)
    elif nowts > TS_DATE_END_START:
        logger.info("现在是晚上上打卡时间")
        get_sign_hs(WS_DATE_START, WS_DATE_END)
    else:
        logger.info("计划时间外！")

def getCookie():
    logger.info('当前时区'+time.strftime('%Z', time.localtime()))
    logger.info("开始获取Cookie")
    result = s.post(LOGIN_URL, LOGIN_PARAM)
    N_COOKIE['sid'] = result.request.headers['Cookie'].split(';')[0].split('=')[1]
    logger.info("Cookie获取完毕，cookie为"+N_COOKIE['sid'])

if __name__ == '__main__':
    # app.run()
    getCookie()
    main()
