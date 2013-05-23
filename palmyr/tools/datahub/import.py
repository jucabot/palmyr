# -*- coding: utf-8 -*-

from settings import CONTEXT
from pyelasticsearch import ElasticSearch
import sys
import cjson

def delete_all():
    es = ElasticSearch(CONTEXT['datahub-store'])
    es.delete_index(CONTEXT['datahub-index'])


    
    
def load(filename,index_name,type_name,category,zone="France",sep=";",display="timeline", source='',description=''):
    
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
         "source" : source,
         'description' : description % (key),
         "data" : {'series':[{'name': key, 'data':map(lambda (k,v) : [k,v],value.items())}]}
         }
        es.index(index_name, display, serie)

    
    es.refresh(index_name)
    f.close()

def load2(filename,index_name,type_name,category,zone="France",sep=";",display="timeline",source='',description=''):
    
    f = open(filename,mode='r')
    es = ElasticSearch(CONTEXT['datahub-store'])

    for line in f:
        key, string_value = line.split(sep,2)
        value = cjson.decode(string_value)
        
        if sum(value.values()) == 0: #remove emptie serie
            continue
        
        key = value['label']
        serie = {
         "name" : key,
         "owner" : "public",
         "display": display,
         "zone": zone,
         "category" : category,
         "source" : source,
         'description' : description % (key),
         "data" : {'series':[{'name': key, 'data':map(lambda (k,v) : [k,v],value.items())}]}
         }
        es.index(index_name, display, serie)

    
    es.refresh(index_name)
    f.close()

def load_wordcloud(filename,index_name,type_name,category,name,zone="France",sep=";",display="wordcloud",source='',description=''):
    
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
     "source" : source,
     'description' : description % (name),
     "data" : { 'categories': map(lambda item : item[0],categories), 'series': [{'data': map(lambda item : item[1],categories)}]  }
     }
    es.index(index_name, display, serie)

    
    es.refresh(index_name)
    f.close()

def load_pie(filename,index_name,type_name,category,name,zone="France",sep=";",display="pie",source='',description=''):
    
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
     "source" : source,
     'description' : description % (key),
     "data" : { 'categories' : categories.keys(), 'series' : [{'data' :  categories.values()}] }
     }
    es.index(index_name, display, serie)

    
    es.refresh(index_name)
    f.close()


    
    es.refresh(index_name)
    f.close()


IMPORT_DIR = '/home/predictiveds/Dropbox/palmyr-data/import datahub/' 

delete_all()

load(IMPORT_DIR + "all_socio_economic.txt",CONTEXT['datahub-index'],"serie",u"Economie",source='Insee',description=u'Evolution mensuelle de %s')
load(IMPORT_DIR + "gtrends.txt",CONTEXT['datahub-index'],"serie","Santé",source=u'Google',description=u'Evolution mensuelle des recherches de %s sur Google')
load_wordcloud(IMPORT_DIR + "word_count_full.txt.top200",CONTEXT['datahub-index'],"serie",u"Santé","Termes les plus utilisés",source=u'Doctissimo.com',description=u'200 %s sur les forums')
load_pie(IMPORT_DIR + "forum_count_full.csv",CONTEXT['datahub-index'],"serie",u"Santé",u"Répartition des messages par forums",source="Doctissimo.com",description=u"%s en nombre")
load(IMPORT_DIR + "labelled_word_series_full.top200.txt",CONTEXT['datahub-index'],"serie",u"Santé",source='Doctissimo',description=u"Evolution mensuelle de l'utilisation du terme %s")
