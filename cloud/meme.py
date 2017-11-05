from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
import os
import sys
import json
import re

import http.client, urllib.request, urllib.parse, urllib.error, base64

sys.path.append("..")
from memeclassifier.scripts.label_image import Meme


@csrf_exempt
def meme(request):
    try:
        if request.method == "POST":
            image = request.FILES.get('image')
            if image == None:
                return HttpResponse('file not existing in the request')
            filename = image.name
            filepath = "/home/ubuntu/djdir/cloud/memeclassifier/src/"+filename
            #filepath = "/var/www/html/picdir/"+filename
            with open(filepath, 'wb') as fobj:
                for chrunk in image.chunks():
                    fobj.write(chrunk)
            fn = filepath
            #cognitive emotion api
            data = open(filepath, 'rb')
            headers = {
                'Content-Type': 'application/octet-stream',#bin stream
                'Ocp-Apim-Subscription-Key': '96001cc4a6414673896ed0e6fab2b501',
            }
            params = urllib.parse.urlencode({})
            try:
                conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
                conn.request("POST", "/emotion/v1.0/recognize?%s" % params, headers=headers ,body=data)
                response = conn.getresponse()
                res = response.read().decode('utf-8')

                p = re.compile(r'\"scores\"\:({.*?})')
                scores = p.findall(res)
                if len(scores)>0:
                    dic  = json.loads(scores[0])
                    for key,value in dic.items():
                        dic[key] = '{:.10f}'.format(value)

                    score = json.dumps(dic)
                    respon = HttpResponse(score)
                    respon['Access-Control-Allow-Origin'] = '*'
                    return respon
                #[{"faceRectangle":{"height":132,"left":44,"top":30,"width":132},"scores":{"anger":0.271403879,"contempt":0.0149730509,"disgust":0.007624591,"fear":0.000333054457,"happiness":0.5846122,"neutral":0.118239768,"sadness":0.002419422,"surprise":0.000394062052}}]
            except Exception as e:
                return HttpResponse(str(e))

            mf ="/home/ubuntu/djdir/cloud/memeclassifier/tf_files/retrained_graph.pb"
            res = Meme.memeclassifier(fn,mf)
            dic = {}
            for key,value in res.items():
                dic[key] = '{:.10f}'.format(value)
            body = json.dumps(dic)
            respon = HttpResponse(body)
            respon['Access-Control-Allow-Origin']='*'
            return respon
        else:
            return HttpResponse("no post")
    except Exception as e:
        return HttpResponse(str(e))

def form(request):
    return render(request, "form.html")
