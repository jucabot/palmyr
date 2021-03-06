
from settings import CONTEXT
from pyelasticsearch import ElasticSearch
import cjson

def dump_as_index_file():
    
    es = ElasticSearch(CONTEXT['datahub-store'])
    
    total = es.count("owner:public AND display:timeline",index=CONTEXT['datahub-index'],doc_type='_all')
    
    series = es.search("owner:public AND display:timeline",index=CONTEXT['datahub-index'],size=total['count'],doc_type='_all')
    
    f = open(CONTEXT['correlation-index-path'],mode='w')
    
    for serie in series['hits']['hits']:
        f.write("%s;%s;%s;%s\n" % (serie['_id'],serie['_source']['name'],cjson.encode(serie['_source']['data']['series'][0]['data']),serie['_source']['category']))
    f.close()
    
    
    

dump_as_index_file()
    