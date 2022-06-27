# -*- coding:utf-8 -*-
import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import HttpResponse

from SignIn.models import User, Sign, SignTotal
import requests
import json

from SignIn.utils import utils

from constants import QRCODE_URL, QR_CODE_HEADER, SIGN, PASSPORT_URL, LOGIN_URL, BDUSS, CHANNEL_V, API_ERROR, \
    API_SUCCESS, API_TIPS


def index(request):
    return render(request, 'index.html')


def get_img(request):
    res = requests.get(url=QRCODE_URL, headers=QR_CODE_HEADER).json()
    return JsonResponse(res)


def new(request):
    sign = request.GET.get(SIGN)
    url = PASSPORT_URL.format(sign)
    try:
        res = requests.get(url=url, headers=QR_CODE_HEADER, timeout=2)
    except requests.exceptions.Timeout:
        fuck = HttpResponse("你没扫码你点尼玛的扫码成功呢？")
        fuck.status_code = 404
        return fuck
    res = res.text[1:-2]
    data = json.loads(res)
    data = json.loads(data[CHANNEL_V])
    v = data['v']
    url3 = LOGIN_URL.format(
        v)
    response = requests.get(url3, timeout=2)
    bduss = response.cookies[BDUSS]
    if not bduss:
        fuck = HttpResponse("你没扫码你点尼玛的扫码成功呢？")
        fuck.status_code = 404
        return fuck
    User.objects.new(bduss)
    return HttpResponse('ok')


def status(request):
    user_count = User.objects.count()
    today_sign = Sign.objects.filter(is_sign=1).exclude(status="").count()
    total_sign = SignTotal.objects.first().number
    return JsonResponse({"user_count": user_count, "today_sign": today_sign, "total_sign": total_sign})


def api_budss(request):
    bduss = request.GET.get("bduss")
    if not bduss:
        return JsonResponse(API_TIPS)
    if len(bduss) != 192:
        return JsonResponse(API_ERROR)
    is_valid = utils.check_bduss(bduss)
    if not is_valid:
        return JsonResponse(API_ERROR)
    User.objects.new(bduss)
    return JsonResponse(API_SUCCESS)

## 增加第三迭代内容
def process_request(self, request):
    return None

def process_response(self, request, response):
    data = dict()
    data['code'] = response.status_code
    content_type = response.content_type if 'Content-Type' not in response else response['Content-Type']
    if content_type == 'application/json':
        if response.status_code == 200:
            data['data'] = response.data
            data['msg'] = '请求成功'
        elif response.status_code == 201:
            data['data'] = response.data
            data['msg'] = "创建成功"
        else:
            data['data'] = []
            data['msg'] = response.data['detail']

        return JsonResponse(data)
    if response.status_code == 204:
        data['data'] = []
        data['msg'] = '删除成功'
        return JsonResponse(data)
    return response
