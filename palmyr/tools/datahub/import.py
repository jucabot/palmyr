# -*- coding: utf-8 -*-

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
        
        if sum(value.values()) == 0: #remove emptie serie
            continue
        
        if 'Undefined-01' in value:
            del value['Undefined-01']
        
        serie = {
         "name" : key,
         "owner" : "public",
         "display": display,
         "zone": zone,
         "category" : category,
         "data" : {'series':[{'name': key, 'data':map(lambda (k,v) : [k,v],value.items())}]}
         }
        es.index(index_name, type_name, serie,id=key)

    
    es.refresh(index_name)
    f.close()

def load2(filename,index_name,type_name,category,zone="France",sep=";",display="timeline"):
    
    f = open(filename,mode='r')
    es = ElasticSearch(CONTEXT['datahub-store'])

    for line in f:
        key, string_value = line.split(sep,2)
        value = cjson.decode(string_value)
        
        if sum(value.values()) == 0: #remove emptie serie
            continue
        
        serie = {
         "name" : value['label'],
         "owner" : "public",
         "display": display,
         "zone": zone,
         "category" : category,
         "data" : {'series':[{'name': value['label'], 'data':map(lambda (k,v) : [k,v],value.items())}]}
         }
        es.index(index_name, type_name, serie,id=value['label'])

    
    es.refresh(index_name)
    f.close()

def load_wordcloud(filename,index_name,type_name,category,name,zone="France",sep=";",display="wordcloud"):
    
    f = open(filename,mode='r')
    es = ElasticSearch(CONTEXT['datahub-store'])

    categories = []
    for line in f:
        key, string_value = line.split(sep,2)
        value = cjson.decode(string_value)
        
        categories.append((value['label'],value['norm_count']/100.0))

    serie = {
     "name" : name,
     "owner" : "public",
     "display": display,
     "zone": zone,
     "category" : category,
     "data" : { 'categories': map(lambda item : item[0],categories), 'series': [{'data': map(lambda item : item[1],categories)}]  }
     }
    es.index(index_name, type_name, serie,id=name)

    
    es.refresh(index_name)
    f.close()

def load_pie(filename,index_name,type_name,category,name,zone="France",sep=";",display="pie"):
    
    f = open(filename,mode='r')
    es = ElasticSearch(CONTEXT['datahub-store'])

    categories = {}
    for line in f:
        key, string_value = line.split(sep,2)
        value = cjson.decode(string_value)
        
        categories[key] = value

    serie = {
     "name" : name,
     "owner" : "public",
     "display": display,
     "zone": zone,
     "category" : category,
     "data" : { 'categories' : categories.keys(), 'series' : [{'data' :  categories.values()}] }
     }
    es.index(index_name, type_name, serie,id=name)

    
    es.refresh(index_name)
    f.close()


delete_all()
load("/home/predictiveds/palmyr-data/import datahub/all_socio_economic.txt","datahub","serie","Economie")
load("/home/predictiveds/palmyr-data/import datahub/gtrends.txt","datahub","serie","Recherche Google")
load_wordcloud("/home/predictiveds/palmyr-data/import datahub/word_count_full.txt.top200","datahub","serie","Doctissimo","mots clefs doctissimo")
load_pie("/home/predictiveds/palmyr-data/import datahub/forum_count_full.csv","datahub","serie","Doctissimo",u"Répartition des messages doctissimo par forums")
load("/home/predictiveds/palmyr-data/import datahub/word_series_full.top200.txt","datahub","serie","Doctissimo")
