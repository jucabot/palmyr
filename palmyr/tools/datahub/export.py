from settings import CONTEXT
from pyelasticsearch import ElasticSearch
import cjson
import datetime

def export_serie(id,output):
    
    result = []
    es = ElasticSearch(CONTEXT['datahub-store'])
    
    series = es.get(CONTEXT['datahub-index'],'_all',id)['_source']['data']['series'][0]['data']
    
    
    for key,value in series:
        date = datetime.datetime.strptime(key,'%Y-%m-%d')
        output.write("%s/%s/%s,%s\n" % (date.month,date.day,date.year,value))
    
   
    

export_serie("7cVs4vgoTveAItND8xR4_w", open("/home/predictiveds/montant_par_date.csv",mode='w'))