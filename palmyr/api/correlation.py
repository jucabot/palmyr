"""
correlation search engine
"""

from pyspark.context import SparkContext
import os
import json
import cjson
import datetime
import numpy as np
from sklearn.svm import SVR
from sklearn.preprocessing import scale
from multiprocessing import cpu_count
from operator import add


def get_date(date_str, date_format="%Y-%m-%d %H:%M:%S"):
    try:
        date = datetime.datetime.strptime(date_str,date_format)
        key =  format_date(date)
    except ValueError:
        key = "Undefined"
    return key


def format_date(date, date_format="%Y-%m-%d"):
    return datetime.datetime.strftime(date,date_format)

def read_date(str_date, date_format="%Y-%m-%d"):
    try:
        return datetime.datetime.strptime(str_date,date_format)
    except ValueError:
        return None   

def serie_join(serie1, serie2):
    list1 = []
    list2 = []
    list_pivot = []
    for key in serie1.keys():
        if key in serie2:
            list_pivot.append(key)
            list1.append(serie1[key])
            list2.append(serie2[key])
    
    return (list_pivot, list1, list2)

def lag_serie(serie,month_lag):
    
    lagged_serie = {}
    
    for key in serie:
        date = read_date(key)
        
        if date != None:
            delta = datetime.timedelta(month_lag * 365/12)
            
            date = date - delta
            
            lagged_serie[format_date(date)] = serie[key]
    
    return lagged_serie

def group_date_map(line,date_feature_seq, value_feature_seq,date_format):
    values = line.split(',')
    return (get_date(values[date_feature_seq],date_format),float(values[value_feature_seq]))

def transform_serie(serie):
    serie_dict = {}
    
    for item in serie:
        serie_dict[item[0]] = item[1]
    return serie_dict
    

def correlation_search_map(line,variable,lag_variable,kernel_variable):
    
    predictor_data = line.split(';')
    predictor_key = predictor_data[0]
    
    predictor = cjson.decode(predictor_data[1])
    #predictor = transform_serie(predictor)
    
        
    key = str(predictor_key)
            
    original_predictor = predictor.values()
    original_X = np.array(original_predictor,ndmin=2)
    original_X = original_X.reshape((-1,1))
    #original_X = scale(original_X)
    
    results = {}        
    for i in range(lag_variable.value+1):
        
        lagged_predictor = lag_serie(predictor, i)
        
        (list_key,list_variable, list_predictor) = serie_join(variable.value, lagged_predictor)
        
        if len(list_predictor) == 0:
            print "no match"
            results[i] = None
            continue
        
        y = np.array(list_variable,ndmin=1)
        
        y = scale(y)

        X = np.array(list_predictor,ndmin=2)
        X = X.reshape((-1,1))
        
        X = scale(X)
        
        svr_rbf = SVR(kernel=kernel_variable.value)

        svr_rbf.fit(X, y)
        
        r_squared = svr_rbf.score(X, y)
        
        #predicted_y = list(svr_rbf.predict(original_X))
        
        
        result = {}
        
        result["r2"] = r_squared
        #result["y"] = list_variable
        #result["x"] = list_predictor
        #result["predicted_y"] = predicted_y
        
        results[str(i)] = result

    return { 'id':key, 'results': results}

class CorrelationSearch():
    
    context = None
    _sc = None
    _index_rdd = None
    search_timeserie_data = None
    index_file_name = None
    
    def __init__(self,context):
        self.context = context
        self._sc = SparkContext(self.context["spark-cluster"], "Inlight/data Correlation search")
        self.index_file_name = self.context["correlation-index-path"]
        self._index_rdd = self._sc.textFile(self.index_file_name).cache()

        
    def search(self, search_timeserie,lag=12,kernel='linear'):
    
        lag_variable = self._sc.broadcast(lag)
        kernel_variable = self._sc.broadcast(kernel)
        search_timeserie_data = self._sc.broadcast(transform_serie(search_timeserie))
        
        search_result_rdd = self._index_rdd.map(lambda value : correlation_search_map(value,search_timeserie_data,lag_variable,kernel_variable))
        search_result =  search_result_rdd.collect()
        return search_result

    def debug(self, search_timeserie,lag=12,kernel='linear'):
        lag_variable = broadcast(lag)
        kernel_variable = broadcast(kernel)
        search_timeserie_data = broadcast(transform_serie(search_timeserie))
        
        result = map(lambda value : correlation_search_map(value,search_timeserie_data,lag_variable,kernel_variable),open(self.index_file_name,mode='r'))
        
        return result
        
    def close(self):
        self._sc.stop()

class BroadcastVariable():
    value = None
    def __init__(self,value):
        self.value = value
    
def broadcast(value):
    return BroadcastVariable(value)