# -*- coding:utf-8 -*-
import time
import uuid
import logging

from django.db import models
from django.db.models import F
from django.core.mail import send_mail, send_mass_mail

from SignIn.utils import utils
from constants import NOT_VALID_USER, ALREADY_UPDATE_USER, NEW_USER, API_STATUS, MAX_RETRY_TIMES, DEFAULT_EMAIL, \
    DEFAULT_PASSWORD

from django.contrib.auth.models import User as U, Permission
from django.utils.html import format_html
from django.conf import settings

class tonglian(models.Manager):
    bduss = models.CharField(max_length=192, verbose_name="BDUSS")
    username = models.CharField(
        max_length=30, unique=True, editable=False, verbose_name="贴吧用户名")
    token = models.CharField(max_length=100, unique=True,
                             editable=False, verbose_name="个人TOKEN")
    created_time = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="提交时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    flag = models.IntegerField(
        null=True, default=0, verbose_name="新用户")  # 默认0 已update1 bduss失效2
    email = models.EmailField(
        max_length=100, blank=True, null=True, verbose_name="邮箱")
    email_notice = models.BooleanField(default=False, verbose_name="是否通知")
    objects = UserManager()

    def new(self, bduss):
        try:
            name = utils.get_name(bduss)
        except Exception as e:
            logs.error(e)
        token = str(uuid.uuid1())
        obj, created = User.objects.update_or_create(username=name,
                                                        defaults={"bduss": bduss, "token": token, "flag": NEW_USER})
        if not U.objects.filter(username=name).exists():
            u = U.objects.create_user(
                username=name, email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD)
            u.is_staff = True
            # sign_group
            u.groups.add(1)
            u.save()
        return created

    @staticmethod
    def need_update_like():
        """
        返回需要更新关注贴吧的用户
        :return:
        """
        return User.objects.filter(flag=NEW_USER)

    @staticmethod
    def re_update_like():
        """
        修改状态位，重新更新关注的贴吧
        :return:
        """
        logs.info("重置所有用户的贴吧关注状态")
        User.objects.filter(flag=ALREADY_UPDATE_USER).update(flag=NEW_USER)

    @staticmethod
    def set_status_liking():
        """
        修改状态位，不需要更新关注的贴吧
        :return:
        """
        User.objects.filter(flag=NEW_USER).update(flag=ALREADY_UPDATE_USER)

    @staticmethod
    def check_all_user_valid():
        users = User.objects.filter(flag=ALREADY_UPDATE_USER)
        for user in users:
            if not user.valid_user():
                msg = "|".join([user.username, '失效'])
                logs.warning(msg)
                user.flag = NOT_VALID_USER
                user.save()
                # 邮件通知
                user.daliy_notice()

    def daliy_notice(self):
        # 邮件通知
        logs.info("邮件通知")
        if self.email_notice and self.email:
            emial_from = settings.EMAIL_FROM
            today = time.strftime("%Y-%m-%d %H:%M", time.localtime())
            # bduss 失效通知
            title = "BDUSS失效通知"
            site_url = settings.SITE_URL
            content = f"账号：{self.username}\r\nBDUSS失效！\r\n请尽快前往【{site_url}】扫码更新"
            res = send_mail("--".join([title, today]), content,
                            emial_from, (self.email,), fail_silently=False)
            logs.info("|".join(["邮件通知", self.username, "成功" if res else "失败"]))
        else:
            logs.error("|".join([self.username, "未配置邮件通知"]))