from settings import CONTEXT
from pyelasticsearch import ElasticSearch
import sys
import cjson

def delete_all():
    es = ElasticSearch(CONTEXT['datahub-store'])
    es.delete_index("datahub")


def load(filename,index_name,type_name,category,zone="France",sep=";",display="timeline"):
    
    f = open(filename,mode='r')
    es = ElasticSearch(CONTEXT['datahub-store'])

    for line in f:
        key, string_value = line.split(sep,2)
        value = cjson.decode(string_value)
        
        serie = {
         "name" : key,
         "owner" : "public",
         "display": display,
         "zone": zone,
         "category" : category, 
         "data" : value
         }
        es.index(index_name, type_name, serie,id=key)

    
    es.refresh(index_name)
    f.close()


delete_all()
load("/home/predictiveds/palmyr-data/import datahub/all_socio_economic.txt","datahub","timeserie","Economie")
load("/home/predictiveds/palmyr-data/import datahub/gtrends.txt","datahub","timeserie","Recherche Google")
