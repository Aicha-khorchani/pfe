import json
from django.shortcuts import render
from django.http import JsonResponse

def api_view(request, *args, **kwargs):
    print(request.body)
    data = json.loads(request.body)
    print(data)
    data['headers']= dict(request.headers)
    data['params']= dict(request.GET)
    data['post-data']=dict(request.POST)
    print(request.headers)
    data['content_type']= request.content_type
    return JsonResponse(data)