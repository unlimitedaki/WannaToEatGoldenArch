from django.http import HttpResponse
from django.shortcuts import render
import json
#import simplejson
def hello(request):
    return HttpResponse("Hello Django")

def hellohtml(request):
    context ={}
    context['hello'] = "hello Django emmmm"
    return render(request,"hello.html",context)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def postdata(request):
    res = {}
    try:
        if request.method == "POST":
            #request.body 为byte 转换为string
            st = request.body.decode("utf-8")
            res = json.loads(st)
            #js = json.dumps(res)

            task = {
                'id':res['id'],
                'name':res['name'],
                'gender':res['gender']
            }
            return HttpResponse('Successed')
        else:
            return HttpResponse("no post ok？")
    except Exception as e:
        return HttpResponse(str(e))