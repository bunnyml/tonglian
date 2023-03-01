from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
from django.http.response import JsonResponse


class MyMiddleware(MiddlewareMixin):

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
        return 