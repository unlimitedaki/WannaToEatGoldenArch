from __future__ import print_function, unicode_literals
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import bosonnlp
@csrf_exempt
def sentence(request):
    name = ['happiness','sadness','anger','fear','contempt','disgust','surprise','neutral']
    posi = [0.9946,0.1305]
    SENTIMENT_URL = 'http://api.bosonnlp.com/sentiment/analysis'
    # 注意：在测试时请更换为您的API Token
    headers = {'X-Token': 'W7L_D08Y.15510.5bmpm711n21j'}
    st = [request.body.decode("utf-8")]
    data = json.dumps(st)
    resp = requests.post(SENTIMENT_URL, headers=headers, data=data.encode("utf-8"))
    res = resp.read()
    pos = resp[0][1]
    return HttpResponse(pos)