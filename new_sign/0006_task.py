from constants import SIGN_WORKER, TIME_SLEEP, LIKE_WORKER
from apscheduler.schedulers.background import BackgroundScheduler
import time
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import django
import os
import sys


# VARIABLE NAME
ERROR_CODE = "error_code"
FORM_LIST = "forum_list"
GCONFORM = "gconforum"
NON_GCONFORM = "non-gconforum"
HAS_MORE = "has_more"
ID = "id"
NAME = "name"
COOKIE = "Cookie"
BDUSS = "BDUSS"
CHANNEL_V = "channel_v"
EQUAL = r'='
EMPTY_STR = r''
TBS = 'tbs'
PAGE_NO = 'page_no'
ONE = '1'
TIMESTAMP = "timestamp"
DATA = 'data'
FID = 'fid'
SIGN_KEY = 'tiebaclient!!!'
UTF8 = "utf-8"
SIGN = "sign"
KW = "kw"
IS_LOGIN = "is_login"

# USER STATUS
NEW_USER = 0
ALREADY_UPDATE_USER = 1
NOT_VALID_USER = 2

parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_path)

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TiebaProject.settings')
django.setup()

# 这里读取了setting配置，所以必须放在django.setup() 后面
from SignIn.models import User, Sign

from django.conf import settings

def update(self):
		url=self.api+"Record.Modify"
		record=self.get_record_list()
		new_ip=self.get_new_ip()
		new_ip=str(new_ip).strip()
		for i in record:
			if(i["value"]==new_ip):
				log = "%s.%s 指向的ip地址未发生变化" %(i["name"],i["domain"])
				self.write_log(log)
				continue
			d=self.data.copy()
			d.update({"domain":i["domain"],"record_id":i["id"],"sub_domain":i["name"],"record_type":"A","record_line":i["line"],"value":new_ip})
			r=json.loads(requests.post(url=url,data=d,headers=self.headers).text)
			if (r["status"]["code"]=="1"):
				log = "%s.%s 成功被指向新的ip地址：%s" % (i["name"],i["domain"],new_ip)
			else:
				log = r["status"]["message"]
			self.write_log(log)



def main():
    # 定时任务相关 （仅作状态更改，具体任务由下方while循环来做）
    scheduler = BackgroundScheduler()
    # 每10点更新一次关注的贴吧
    scheduler.add_job(User.objects.re_update_like, 'cron', hour='10')
    # 每天0点0分重置贴吧的签到状态，进行签到
    scheduler.add_job(Sign.objects.reset_sign_status, 'cron', hour='0')
    # 每天8,12,16点再次签到
    scheduler.add_job(Sign.objects.reset_sign_status_again, 'cron', hour='8,12,16')
    # 检查用户的bduss是否失效,并且邮件通知
    if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD and settings.EMAIL_FROM:
        scheduler.add_job(User.objects.check_all_user_valid, 'cron', hour='9')
    scheduler.start()
    ############################################################################################
    # 后台任务 （签到和更新关注贴吧）
    like = Queue()  # 更新关注队列
    sign = Queue()  # 签到队列
    like_thread_pool = ThreadPoolExecutor(
        max_workers=LIKE_WORKER, thread_name_prefix="like_")  # 初始化线程池数量
    sign_thread_pool = ThreadPoolExecutor(
        max_workers=SIGN_WORKER, thread_name_prefix="sign_")  # 初始化线程池数量
    while True:
        person_like = User.objects.need_update_like()
        for person in person_like:
            like.put(person)
        # 修改标记位，标记已经开始更新关注的贴吧
        if not like.empty():
            User.objects.set_status_liking()

            while not like.empty():
                person = like.get()
                if isinstance(person, User):
                    like_thread_pool.submit(person.like).add_done_callback(
                        person.like_callback)
        # 上面是获取关注贴吧
        ################################################################
        # 下面是对贴吧进行签到
        signs = Sign.objects.need_sign()
        for s in signs:
            sign.put(s)
        # 修改状态位 标记全部开始签到
        if not sign.empty():
            Sign.objects.set_status_signing()

            while not sign.empty():
                s = sign.get()
                if isinstance(s, Sign):
                    sign_thread_pool.submit(
                        s.sign).add_done_callback(s.sign_callback)

        time.sleep(TIME_SLEEP)


if __name__ == '__main__':
    main()