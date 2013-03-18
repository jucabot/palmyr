
        
class UserContext():
    request = None
    params = None
    
    def __init__(self,request):
        self.request = request
        self.params = request.GET
        
    def get_feature_table(self,ftname):    
        return self.request.session['feature_tables:'+ftname]
    
    def set_feature_table(self,ftname,ftable):    
        self.request.session['feature_tables:'+ftname] = ftable

    def feature_table_exist(self,ftname):
        return 'feature_tables:' + ftname in self.request.session
