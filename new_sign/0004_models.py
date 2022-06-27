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

logs = logging.getLogger("task")


class UserManager(models.Manager):

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

class SignLog(models.Model):
    name = models.CharField(max_length=100, verbose_name="贴吧名")
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="所属用户")
    ret_log = models.TextField(verbose_name="签到日志")
    objects = SignLogManager()

    class Meta:
        db_table = 'sign_log'
        ordering = ['-update_time']
        verbose_name = '签到日志'
        verbose_name_plural = verbose_name


class SignTotal(models.Model):
    number = models.IntegerField()

    class Meta:
        db_table = 'sign_total'
        verbose_name = '签到总数'
        verbose_name_plural = verbose_name