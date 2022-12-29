from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render

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