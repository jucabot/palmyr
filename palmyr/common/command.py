from django.http import HttpResponse
import cjson
import json
from django.core.cache import cache

def success(**kwargs):
    response = { "status":'success'}
    response.update(kwargs)
    try:
        return HttpResponse(cjson.encode(response))
    except:
        return HttpResponse(json.dumps(response))
    
def error(message):
    return HttpResponse(cjson.encode({ "status":"error" , "message":"%s" % str(message)}))



class Command():
    ctx = None
    def __init__(self,context):
        self.ctx = context
    
    def success(self,**kwargs):
        response = { "status":'success'}
        response.update(kwargs)
        try:
            return HttpResponse(cjson.encode(response))
        except:
            return HttpResponse(json.dumps(response))
    
    def error(self,message):
        return HttpResponse(cjson.encode({ "status":"error" , "message":"%s" % str(message)}))

