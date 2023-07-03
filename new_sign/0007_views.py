from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render
import pymysql

def index(request):
    return render(request, '1.html')


class MyPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class SnippetList(ListCreateAPIView):
    serializer_class = SnippetSerializer
    pagination_class = MyPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        a = self.request.query_params.dict()
        del_key = []
        for k in a.keys():
            key = getattr(Snippet, k, None)
            if key is None:
                del_key.append(k)
        for key in del_key:
            del a[key]
        return Snippet.objects.filter(**a)


class SnippetDetailAndDestroy(RetrieveUpdateDestroyAPIView):
    serializer_class = SnippetSerializer
    queryset = Snippet.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
# 修改数据库配置信息
config={"host":"localhost", 
			"port":3306,
			"user":"mysql",
			"passwd":"",
			"db":"test",
			"charset":'utf8'}

def lib_insert(i,h,**config):
	# i是lib()返回的read_info,h是lib()返回的read_his
	conn = pymysql.connect(**config)
	cur = conn.cursor()
	sql = r"INSERT INTO `lib_info` VALUES(NULL,'"+i['读者证件号']+"','"+i['姓名']+"','"+i['性别']+"','"+i['读者条码号']+"','"+i['读者类型']\
			+"','"+i['工作单位']+"','"+i['职业']+"','"+i['职称']+"','"+i['职位']+"','"+i['生效日期']+"','"+i['失效日期']\
			+"','"+i['押金']+"','"+i['手续费']+"','"+i['累计借书']+"','"+i['违章状态']+"','"+i['欠款状态']+"')"
	cur.execute(sql)
	for l in h:
		sql = "INSERT INTO `lib_his` VALUES('"+l[0]+"','"+l[1]+"','"+l[2]+"','"+l[3]+"','"+l[4]+"','"+l[5]+\
		"','"+l[6]+"')"
		try:
			cur.execute(sql)
		except:
			pass
	conn.commit()
	cur.close()
	conn.close()
def finance_insert(*i):
	# 这个数据库不会建
	pass