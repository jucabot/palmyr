from django.http import HttpResponse
import cjson


class Command():
    ctx = None
    def __init__(self,context):
        self.ctx = context
    
    
    def success(self,**kwargs):
        response = { "status":'success'}
        response.update(kwargs)
        return HttpResponse(cjson.encode(response))

    def error(self,message):
        return HttpResponse(cjson.encode({ "status":"error" , "message":"%s" % str(message)}))
