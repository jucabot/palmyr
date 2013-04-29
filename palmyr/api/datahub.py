from pyelasticsearch import ElasticSearch,ElasticHttpNotFoundError

class Datahub():
    
    context = None
    _es = None
    index = None
    user_id = None
    
    def __init__(self,context,index=None,user_id=None):
        self.context = context
        self._es = ElasticSearch(self.context['datahub-store'])
        self.index = index if index is not None else self.context['datahub-index']
        self.user_id = user_id
        
    def _get_user_id(self):
        self.user_id = "user_%s" % (self.user_id)  
        
    def query(self,name,type_name="serie"):
        if self.user_id is None:
            q = '%s AND owner:public' % name
        else:
            q = '%s AND (owner:public OR owner:"%s")' % (name,self._get_user_id())
        results= self._es.search(q,index=self.index,doc_type=type_name)
        
        if results['hits']['total'] > 0:
    
            return map(lambda s : s['_source'],results['hits']['hits'])
        else:
            return None
        
    def get(self,key,type_name="serie"):
        try:
            result = self._es.get(self.index,type_name,id=key)
            if result['_source']['owner'] == 'public' or result['_source']['owner'] == self._get_user_id():
                return result['_source']
            else:
                return None
        
        except ElasticHttpNotFoundError:
            return None
       
       
        
        