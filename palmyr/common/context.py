import os
from os import path
from settings import CONTEXT
        
class UserContext():
    request = None
    params = None
    user = None
    
    def __init__(self,request):
        self.request = request
        self.params = request.GET
        self.user = request.user
        
    def get_feature_table(self,ftname):
        ftable = self.request.session['feature_tables:'+ftname].load()
        return ftable
    
    def set_feature_table(self,ftname,ftable):
            
        self.request.session['feature_tables:'+ftname] = ftable.save()

    def feature_table_exist(self,ftname):
        return 'feature_tables:' + ftname in self.request.session

    def get_user_root(self,base=CONTEXT['data-root']):
        user_dir = base + os.sep + str(self.user.id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return path.normpath(user_dir)