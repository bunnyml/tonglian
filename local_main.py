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
MAIN_URL = "http://125.35.5.51/cap-aco-bx/"

LOGIN_URL = "login"
USER_SIGN_URL = "signInMobileController/doSaveSignIn"
SIGN_HS_URL = "signInController/findSignInInfoByCondition"


local_name = "%e5%8c%97%e4%ba%ac%e5%90%8c%e8%81%94%e4%bf%a1%e6%81%af%e6%8a%80%e6%9c%af%e6%9c%89%e9%99%90%e5%85%ac%e5%8f%b8"
local_address = "%e5%8c%97%e6%b8%85%e8%b7%af68%e5%8f%b7%e9%99%a22%e5%8f%b7%e6%a5%bc2%e5%b1%8258%e5%ae%a4"
# userId
user_code = "75ca4ebc7cef402cbb453d0a97756467"
# 登录账号
ACCT_LOGIN = "yz"
# 密码
PASSWORD = "yy616499"
# 签到用户名 这里使用的是URL编码后的用户名
USER_NAME = "%e6%9d%a8%e5%93%b2"
# 查询签到记录用户名
QUERY_USER_NAME = "杨哲"
# 打卡状态 1:执行打卡任务  2:不执行打卡任务
SIGN_STATE = "1"

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
    'sid':'',
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
ZS_END_TIME = time.strftime('%Y-%m-%d',time.localtime())+' 09:30:00'
WS_START_TIME = time.strftime('%Y-%m-%d',time.localtime())+' 17:30:00'
WS_END_TIME = time.strftime('%Y-%m-%d',time.localtime())+' 21:30:00'

# Header
HEADERS = {
    'Host':'125.35.5.51',
    'Content-Type': 'text/plain;charset=UTF-8'
}

def signIn():
    result = s.get(url=MAIN_URL+USER_SIGN_URL, cookies=N_COOKIE, params=PARAME_DATA, headers=HEADERS)
    text = result.json()
    if text['result'] == 0:
        logger.info("打卡成功")
        push_wechat()

def setCookie():
    logger.info("开始获取Cookie")
    result = None
    try:
        result = s.post(url=MAIN_URL+LOGIN_URL, params=LOGIN_PARAM, timeout=30)
        url = str(result.url)
        N_COOKIE['sid'] = result.request.headers['Cookie'].split(';')[0].split('=')[1]
        logger.info("Cookie替换完毕，cookie为"+N_COOKIE['sid'])
    except requests.exceptions.ConnectionError as e:
        if result is not None:
            result.connection.close()
        logger.info("获取SID连接异常，服务器拒绝连接！")
        logger.info(str(e))
        logger.info("开始重新获取Cookie")
        setCookie()
   

# 1、根据给定的时间段，查询打卡记录
# 2、打过卡则跳过  未打过卡就开始执行自动打卡
def get_sign_hs(start, end):
    setCookie()
    logger.info("Cookie设置完毕！开始获取打卡记录，开始时间："+start+"  结束时间："+end)
    SIGN_HS_DATE['queryStartTime'] = start
    SIGN_HS_DATE['queryEndTime'] = end
    try:
        result = s.get(url=MAIN_URL+SIGN_HS_URL, cookies=N_COOKIE, params=SIGN_HS_DATE, headers=HEADERS,  timeout=5)
        url = str(result.url)
        logger.info("resut的url是"+url)
        if bool(re.search('cap-aco-bx/login',url)) == False:
            logger.info("cookie正常，开始判断是否需要打卡！")
            returnData = result.json()
            if returnData['rows'] != []:
                logger.info("本时段打过卡了")
            else:
                signIn()
                logger.info("没有查询到打卡记录，开始自动打卡！")
        else:
            logger.info("cookie过期了！开始执行重新登录！")
            setCookie()
            logger.info("已重新登录！SID值为"+N_COOKIE['sid']+"，准备重新打卡")
            get_sign_hs(start, end)
    except Exception as e:
        logger.info("程序异常了，请检查！程序异常了，请检查！")

#主方法
# 1、判断今天是不是工作日
# 2、判断当前时间属于早上打卡还是晚上打卡
# 3、查询当前时间段的打卡记录 早上时间段8:01-9:25  晚上时间段17:30-21:30
def main():
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    #判断是否是启用状态
    if SIGN_STATE != '1':
        logger.info("没有启用打卡任务")
        return
    #判断今天是否是工作日
    if dateState() == False:
        logger.info("今天不是工作日不需要打卡")
        return
    logger.info("工作日，开始判断当前是早上打卡还是晚上打卡")
    ZS_START_DATETIME = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 00:01:00', "%Y-%m-%d %H:%M:%S")))
    ZS_END_DATETIME = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 01:30:00', "%Y-%m-%d %H:%M:%S")))
    WS_START_DATETIME = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 07:30:00', "%Y-%m-%d %H:%M:%S")))
    WS_END_DATETIME = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 13:30:00', "%Y-%m-%d %H:%M:%S")))

    NOW_DATETIME = int(time.time())
    # NOW_DATETIME = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime())+' 08:38:00', "%Y-%m-%d %H:%M:%S")))
    
    logger.info("UTC当前时间为"+time.strftime('%Y-%m-%d %H:%M:%S'))
    # 注意这里判断的时间全是UTC时间
    if NOW_DATETIME > ZS_START_DATETIME and NOW_DATETIME < ZS_END_DATETIME:
        logger.info("现在是早上打卡时间")
        get_sign_hs(ZS_START_TIME, ZS_END_TIME)
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

PUSH_URL = "https://sc.ftqq.com/SCU112622Td6ab1713c2c49f53019938b14b42c8055f564265d31e7.send"

def push_wechat():
    logger.info("开始执行微信推送")
    ndate = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    WECHAT_PARAM = {
        'text':ndate + "-执行了一次自动打卡任务",
        'desp': "系统执行了一次打卡任务，时间是" + ndate 
    }
    s.post(PUSH_URL, WECHAT_PARAM)

if __name__ == '__main__':
    main()
