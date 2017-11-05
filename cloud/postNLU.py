
from django.shortcuts import render
from django.http import HttpResponse
import hashlib
import random
import urllib.request
import urllib.parse
import json

def translator(text):
	appKey = '75a4340187f5410d'
	secretKey = '9M76fBESqsfcPSLDDcPZDyhhthzhscgY'
	httpClient = None
	myurl = 'https://openapi.youdao.com/api'
	q = text
	fromLang = 'zh-CHS'
	toLang = 'EN'
	salt = random.randint(1, 65536)
	sign = appKey+q+str(salt)+secretKey
	m1 = hashlib.md5()
	m1.update(sign.encode('utf-8'))
	sign = m1.hexdigest()
	myurl = myurl+'?appKey='+appKey+'&q='+urllib.parse.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign
	myurl = str(myurl)
	try:
		request = urllib.request.Request(myurl)
		f = urllib.request.urlopen(request)
		fdata = f.read().decode("utf-8")
		resultlist = json.loads(fdata)
	except Exception as e:
		resultlist = {'translation':'nothing'}

	return resultlist['translation']

def getNLU(request):
	text = request.body.decode("utf-8")
	text = text.split("\"")[3]
	tran = translator(text)[0]
	# return HttpResponse(tran)
	Authorization="Basic YTYyY2JiMzUtZGYyOC00NjE1LWJhYTAtYTZlZTUxYjhiODljOlRuSDhydWVlOE5FSQ=="
	emotiondic = dict(zip(["happy","fear","disgust","anger","sadness","neutral","contempt","surprise"],(0,0,0,0,0,0,0,0)))
	body = {
    "text": tran,
    "features": {
      "entities": {
        "emotion": True,
        "sentiment": True,
      },
      "keywords": {
        "emotion": True,
        "sentiment": True,
    }
  }
}
	data = json.dumps(body)
	data = data.encode('utf-8')
	request = urllib.request.Request("https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2017-02-27")
	request.add_header("Content-Type","application/json")
	request.add_header("Authorization", Authorization)
	try:
		f = urllib.request.urlopen(request,data)
		fdata = f.read().decode("utf-8")
		resultlist = json.loads(fdata)["keywords"]

		for item in resultlist:
			if ('emotion' in item):

				emotiondic["happy"] += item['emotion']['joy']
				emotiondic["sadness"] += item['emotion']["sadness"]
				emotiondic["fear"] += item['emotion']["fear"]
				emotiondic["anger"] += item['emotion']["anger"]
				emotiondic["disgust"] += item['emotion']["disgust"]
				emotiondic["surprise"] += (0.29*item['emotion']['joy']+0.05*item['emotion']['anger']+0.37*item['emotion']['disgust']+0.09*item['emotion']['sadness']+0.06*item['emotion']['fear'])
				emotiondic["neutral"] += (0.2*item['emotion']['joy']+0.2*item['emotion']['anger']+0.2*item['emotion']['disgust']+0.2*item['emotion']['sadness']+0.2*item['emotion']['fear'])
				emotiondic["contempt"] += (0.27*item['emotion']['joy']+0.05*item['emotion']['anger']+0.15*item['emotion']['disgust']+0.08*item['emotion']['sadness']+0.05*item['emotion']['fear'])
			else:
				continue
		sigma = sum(emotiondic.values())
		if sigma:
			emotiondic["happy"] /= sigma
			emotiondic["sadness"] /= sigma
			emotiondic["fear"]  /= sigma
			emotiondic["anger"] /= sigma
			emotiondic["disgust"] /= sigma
			emotiondic["surprise"] /= sigma
			emotiondic["neutral"] /= sigma
			emotiondic["contempt"]/= sigma
		for key,value in emotiondic.items():
			emotiondic[key] = '{:.10f}'.format(value)
		# emotiondic["sentence"] = tran
	except Exception as e:
		emotiondic = dict(zip(["happy","fear","disgust","anger","sadness","neutral","contempt","surprise"],("0.125","0.125","0.125","0.125","0.125","0.125","0.125","0.125")))
	finally:
		return HttpResponse(json.dumps(emotiondic))
