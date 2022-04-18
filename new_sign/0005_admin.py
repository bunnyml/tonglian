from django.contrib import admin
from .models import User, Sign, SignLog, SignTotal


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'email_notice', 'token',
                    '共关注', '已签到', '未签到', '是否有效用户', 'created_time', 'update_time')
    list_editable = ('email', 'email_notice')
    search_fields = ('username', 'email')
    list_display_links = ('username',)
    list_per_page = 30
    date_hierarchy = 'created_time'
    actions = ('make_new_user',)

    def make_new_user(self, request, queryset):  # 定义动作
        rows_updated = queryset.update(flag=0)
        if rows_updated == 1:
            message_bit = "one user changed"
        else:
            message_bit = "%s users changed" % rows_updated
        self.message_user(request, "%s successfully ." % message_bit)

    make_new_user.short_description = "刷新关注的贴吧并签到"  # 重写动作显示名称

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(username=request.user.username)


class SignAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'fid', 'is_sign',
                    'retry_time', 'status', 'user')
    search_fields = ('id', 'name', 'fid', 'status', 'user__username')
    actions = ['re_sign', ]

    def re_sign(self, request, queryset):  # 定义动作
        rows_updated = queryset.update(is_sign=0, retry_time=0, status="")
        if rows_updated == 1:
            message_bit = "one tieba resign"
        else:
            message_bit = "%s  tieba resign" % rows_updated
        self.message_user(request, "%s successfully ." % message_bit)

    re_sign.short_description = "重新签到"  # 重写动作显示名称

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        u = User.objects.get(username=request.user.username)
        return qs.filter(user=u)


class SignLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'update_time', 'ret_log', 'user')
    search_fields = ('id', 'name', 'user__username')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        u = User.objects.get(username=request.user.username)
        return qs.filter(user=u)


class SignTotalAdmin(admin.ModelAdmin):
    list_display = ('id', 'number')
    
class Sign(models.Model):
    name = models.CharField(max_length=100, verbose_name="贴吧名")
    fid = models.CharField(max_length=20, verbose_name="贴吧id")
    is_sign = models.BooleanField(default=False, verbose_name="是否签到")
    retry_time = models.SmallIntegerField(default=0, verbose_name="重试次数")
    status = models.CharField(max_length=100, verbose_name="签到状态", default="")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="所属用户")
    objects = SignManager()

    def __str__(self):
        return self.name

    def sign(self):
        u = self.user
        try:
            res = utils.client_sign(bduss=u.bduss, sign=self)
        except Exception as e:
            logs.error(e)
        finally:
            return {"res": res, 'sign': self}

    def sign_callback(self, obj):
        result = obj.result()
        res = result["res"]
        sign = result["sign"]
        # 判断res是否为None,即签到过程中有没有发生异常
        if not res:
            self.objects.update(
                is_sign=False, status="网络发生异常", retry_time=F('retry_time') + 1)
        else:
            # res 为有效值，开始判断签到情况
            error_code = str(res.get('error_code', 0))

            if error_code in API_STATUS:
                self.is_sign = True
                self.status = API_STATUS[error_code]
                # 只有签到成功的时候进行 日志记录
                msg = "|".join(["签到成功", sign.user.username, sign.name])
                logs.info(msg)
                SignLog.objects.log(sign, res)
            else:
                # 如果尝试签到3次还未成功，则不再尝试
                if self.retry_time >= MAX_RETRY_TIMES:
                    self.is_sign = True
                    self.status = "超过最大签到重试次数"
                    # 只有签到成功的时候进行 日志记录
                    SignLog.objects.log(sign, res)
                else:
                    self.is_sign = False
                    self.retry_time += 1
                    self.status = res.get('error_msg', "未知错误")
                msg = '|'.join(
                    ['签到出错', sign.user.username, sign.name, self.status])
                logs.error(msg)
            self.save()

    class Meta:
        db_table = 'sign'
        verbose_name = '签到'
        verbose_name_plural = verbose_name
        unique_together = (('name', 'fid', 'user'),)


class SignLogManager(models.Manager):

    @staticmethod
    def log(sign, ret_log):
        # 写日志
        SignLog.objects.update_or_create(
            name=sign.name, user=sign.user, defaults={"ret_log": ret_log})
        # 更新签到总数
        SignTotal.objects.update(number=F('number') + 1)


admin.site.register(User, UserAdmin)
admin.site.register(Sign, SignAdmin)
admin.site.register(SignLog, SignLogAdmin)
admin.site.register(SignTotal, SignTotalAdmin)
