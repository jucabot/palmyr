from pyelasticsearch import ElasticSearch,ElasticHttpNotFoundError

class Datahub():
    
    context = None
    _es = None
    index_name = None
    user_id = None
    
    def __init__(self,context,index=None,user_id=None):
        self.context = context
        self._es = ElasticSearch(self.context['datahub-store'])
        self.index_name = index if index is not None else self.context['datahub-index']
        self.user_id = user_id
        
    def _get_user_id(self):
        if self.user_id is None:
            return "public"
        else:
            return "user_%s" % (self.user_id)  
        
    def query(self,name,type_name="_all",es_from=0):
        if self.user_id is None:
            q = '%s AND owner:public' % name
        else:
            q = '%s AND (owner:public OR owner:"%s")' % (name,self._get_user_id())
        results= self._es.search(q,index=self.index_name,doc_type=type_name,es_from=es_from)
        
        if results['hits']['total'] > 0:
    
            return (map(lambda s : (s['_id'],s['_source']),results['hits']['hits']),results['hits']['total'],results['took'])
        else:
            return None,results['hits']['total'],results['took']
        
    def get(self,key,type_name="_all"):
        result={}
        try:
            result = self._es.get(self.index_name,type_name,id=key)
            if result['_source']['owner'] == 'public' or result['_source']['owner'] == self._get_user_id():
                return result['_source']
            else:
                return None
        
        except ElasticHttpNotFoundError:
            return None
       
       
    def index(self,name,display_type,data,category="private",source="private",zone="private",description=""):
        
        serie = {
         "name" : name,
         "owner" : self._get_user_id(),
         "display": display_type,
         "zone": zone,
         "category" : category,
         "source" : source,
         'description' : description,
         "data" : data
         }
        
        id = self._es.index(self.index_name, display_type, serie)

        return id['_id']
        