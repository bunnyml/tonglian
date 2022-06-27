# -*- coding:utf-8 -*-

import json
import time
import os
import requests
from django.contrib import admin
from django.urls import path, include

application = get_wsgi_application()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'SignIn',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TiebaProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s : %(message)s'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(module)s %(process)d %(thread)d : %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(LOGGING_DIR, 'task.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 10,
            'mode': 'a',
        },
    },
    'loggers': {  # log记录器，配置之后就会对应的输出日志
        'task': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

WSGI_APPLICATION = 'TiebaProject.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tiebaproject',
        'USER': 'root',
        'PASSWORD': '1BQnsRlwhOE5qfuY',
        'HOST': 'db',
        'PORT': 3306,
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# SESSION
SESSION_COOKIE_AGE = 3600

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25

# 发送邮件的邮箱
EMAIL_HOST_USER = None
# 在邮箱中设置的客户端授权密码（指的是你开启服务时腾讯给的那个授权码）
EMAIL_HOST_PASSWORD = None
# 收件人看到的发件人
EMAIL_FROM = None

# 日志
LOGGING_DIR = "/var/log/tieba"  # 日志存放路径
if not os.path.exists(LOGGING_DIR):
    os.makedirs(LOGGING_DIR, 755);

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('SignIn.urls'))
]

SIGN_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'ka=open',
    'User-Agent': 'bdtb for Android 9.7.8.0',
    'Connection': 'close',
    'Accept-Encoding': 'gzip',
    'Host': 'c.tieba.baidu.com',
}
SIGN_DATA = {
    '_client_type': '2',
    '_client_version': '9.7.8.0',
    '_phone_imei': '000000000000000',
    'model': 'MI+5',
    "net_type": "1",
}

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TiebaProject.settings")

application = get_wsgi_application()

# Others
SITE_URL = "sign.heeeepin.com"


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

def get_record_list(self):
		url=self.api+"Record.List"
		res = []
		for i in self.domain_list:
			data=self.data.copy()
			data.update({"domain":i[0]})
			r=json.loads(requests.post(url=url,data=data,headers=self.headers).text)
			for j in r["records"]:
				if (j["type"]=="A" and j["name"] in i):
					j["domain"]=i[0]
					res.append(j)
		return res

def update(self):
    url=self.api+"Record.Modify"
    record=self.get_record_list()
    new_ip=self.get_new_ip()
    new_ip=str(new_ip).strip()
    for i in record:
        if (r["status"]["code"]=="1"):
            log = "%s.%s 成功被指向新的ip地址：%s" % (i["name"],i["domain"],new_ip)
        else:
            log = r["status"]["message"]
        self.write_log(log)

def write_log(self,content):
    url=self.api+"domain.List"
    t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    content=t+"\t"+content+"\n"
    file=self.path+'/result.log'
    data=self.data.copy()
    data.update({"domain":0})
    with open(file,"a+") as f:
        f.write(content)
        log = "日志打印成功！"
