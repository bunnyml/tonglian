# -*- coding:utf-8 -*-
import requests
import logging
import time
import re
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

s = requests.Session()

#API_URL
# HOST = os.environ['TONGLIAN_HOST']
HOST = '11'
BDUSS = os.environ['BDUSS']
MAIN_URL = "http://"+HOST+"/cap-aco-bx/"

LOGIN_URL = "login"
USER_SIGN_URL = "signInMobileController/doSaveSignIn"
SIGN_HS_URL = "signInController/findSignInInfoByCondition"


local_name = "%e5%8c%97%e4%ba%ac%e5%90%8c%e8%81%94%e4%bf%a1%e6%81%af%e6%8a%80%e6%9c%af%e6%9c%89%e9%99%90%e5%85%ac%e5%8f%b8"
local_address = "%e5%8c%97%e6%b8%85%e8%b7%af68%e5%8f%b7%e9%99%a22%e5%8f%b7%e6%a5%bc2%e5%b1%8258%e5%ae%a4"
# userId
# user_code = "402881b17553294901755361923f0003"
user_code = "75ca4ebc7cef402cbb453d0a97756467"
# 登录账号
ACCT_LOGIN = "yz"
# ACCT_LOGIN = "shifeiduo"
# 密码
PASSWORD = "yy616499"
# PASSWORD = "1234qwer"
# 签到用户名 这里使用的是URL编码后的用户名
USER_NAME = "%e6%9d%a8%e5%93%b2"
# 查询签到记录用户名
QUERY_USER_NAME = "杨哲"

#参数
PARAME_DATA = {
    'pageNum':'0',
    'pageSize':'10',
    'queryUserName':USER_NAME,
    'queryTools':'2',
    'queryStartTime':'',
    'queryEndTime':'',
    'json': '{"version":"2.0.0","compress":"0","encrypt":"0","encode":"1","result":"0","usercode":"'+user_code+'","userId":"'+user_code+'","localName":"'+local_name+'","localAddress":"'+local_address+'","userCode":"'+user_code+'","editContent":""}'
}

#Cookie
N_COOKIE = {
    'sid':'b83ff1ce-517a-491f-a342-c2e0a9327de1',
    'username':ACCT_LOGIN,
    'password':'',
    'rememberme':'0',
    'autoSubmit':'0',
    'sys':'OA'
}

#登录参数
LOGIN_PARAM = {
    'sys':'OA',
    'username':ACCT_LOGIN,
    'password':PASSWORD,
    'rememberme':'0',
    'autoSubmit':'0'
}

#获取自己今天的打卡记录
SIGN_HS_DATE = {
    'pageNum':'0',
    'pageSize':'10',
    'queryUserName':QUERY_USER_NAME,
    'queryTools':'2',
    'queryStartTime':'',
    'queryEndTime':''
}

#时间范围
ZS_START_TIME = time.strftime('%Y-%m-%d',time.localtime())+' 08:01:00'
ZS_END_TIME = time.strftime('%Y-%m-%d',time.localtime())+' 09:25:00'
WS_START_TIME = time.strftime('%Y-%m-%d',time.localtime())+' 17:30:00'
WS_END_TIME = time.strftime('%Y-%m-%d',time.localtime())+' 21:30:00'

# Header
HEADERS = {
    'Host':HOST,
    'Content-Type': 'text/plain;charset=UTF-8'
}

def signIn():
    result = s.get(url=MAIN_URL+USER_SIGN_URL, cookies=N_COOKIE, params=PARAME_DATA, headers=HEADERS)
    text = result.json()
    if text['result'] == 0:
        logger.info("打卡成功")

def setCookie():
    logger.info("开始获取Cookie")
    result = s.post(MAIN_URL+LOGIN_URL, LOGIN_PARAM)
    N_COOKIE['sid'] = result.request.headers['Cookie'].split(';')[0].split('=')[1]
    logger.info("Cookie替换完毕，cookie为"+N_COOKIE['sid'])

# 1、根据给定的时间段，查询打卡记录
# 2、打过卡则跳过  未打过卡就开始执行自动打卡
def get_sign_hs(start, end):
    logger.info("开始获取打卡记录，开始时间："+start+"  结束时间："+end)
    SIGN_HS_DATE['queryStartTime'] = start
    SIGN_HS_DATE['queryEndTime'] = end
    try:
        result = s.get(url=MAIN_URL+SIGN_HS_URL, cookies=N_COOKIE, params=SIGN_HS_DATE, headers=HEADERS,  timeout=5)
        url = str(result.url)
        logger.info("resut的url是"+url)
        if bool(re.search('cap-aco-bx/login',url)) == False:
            returnData = result.json()
            if returnData['rows'] != []:
                logger.info("本时段打过卡了")
            else:
                signIn()
                logger.info("没有查询到打卡记录，开始自动打卡！")
        else:
            logger.info("cookie过期了！", "cookie过期了，请重新设置！")
    except Exception as e:
        logger.info("程序异常了，请检查！", "程序异常了，请检查！")

#主方法
# 1、判断今天是不是工作日
# 2、判断当前时间属于早上打卡还是晚上打卡
# 3、查询当前时间段的打卡记录 早上时间段8:01-9:25  晚上时间段17:30-21:30
def main():
    #判断今天是否是工作日
    if dateState() == False:
        logger.info("今天不是工作日不需要打卡")
        return
    logger.info("工作日，开始判断当前是早上打卡还是晚上打卡")
    ZS_START_DATETIME = int(time.mktime(time.strptime(ZS_START_TIME, "%Y-%m-%d %H:%M:%S")))
    ZS_END_DATETIME = int(time.mktime(time.strptime(ZS_END_TIME, "%Y-%m-%d %H:%M:%S")))
    WS_START_DATETIME = int(time.mktime(time.strptime(WS_START_TIME, "%Y-%m-%d %H:%M:%S")))
    WS_END_DATETIME = int(time.mktime(time.strptime(WS_END_TIME, "%Y-%m-%d %H:%M:%S")))

    NOW_DATETIME = int(time.time())
    # NOW_DATETIME = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 08:38:00', "%Y-%m-%d %H:%M:%S")))

    if NOW_DATETIME > ZS_START_DATETIME and NOW_DATETIME < ZS_END_DATETIME:
        logger.info("现在是早上打卡时间")
        get_sign_hs(ZS_START_TIME, WS_END_TIME)
    elif NOW_DATETIME > WS_START_DATETIME and NOW_DATETIME < WS_END_DATETIME:
        logger.info("现在是晚上上打卡时间")
        get_sign_hs(WS_START_TIME, WS_END_TIME)
    else:
        logger.info("计划时间外！")

def dateState():
    retultData = s.get("http://tool.bitefu.net/jiari/?d="+time.strftime('%Y-%m-%d',time.localtime()))
    if retultData.text == '0':
        return True
    else:
        return False

if __name__ == '__main__':
    # setCookie()
    # main()
    print(HOST)
    print(MAIN_URL)
    print(BDUSS)