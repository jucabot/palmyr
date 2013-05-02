
from settings import CONTEXT
from pyelasticsearch import ElasticSearch
import cjson

def dump_as_index_file():
    
    es = ElasticSearch(CONTEXT['datahub-store'])
    
    total = es.count("owner:public AND display:timeline",index=CONTEXT['datahub-index'],doc_type='serie')
    
    series = es.search("owner:public AND display:timeline",index=CONTEXT['datahub-index'],size=total['count'],doc_type='serie')
    
    f = open(CONTEXT['correlation-index-path'],mode='w')
    
    for serie in series['hits']['hits']:
        f.write("%s;%s\n" % (serie['_id'],cjson.encode(serie['_source']['data']['series'][0]['data'])))
    f.close()
    
    
    

dump_as_index_file()
    