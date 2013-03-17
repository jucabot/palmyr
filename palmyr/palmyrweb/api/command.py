from django.http import HttpResponse
import json
from palmyrweb.views import get_user_root
from settings import ANALYSIS_ROOT, DATA_ROOT
import os
from palmyrdb.converter import TEXT_TYPE, TypeConverter, INT_TYPE, FLOAT_TYPE,\
    NONE_VALUE
from palmyrweb.api.nlquery import nlq_parse
from palmyrdb.core import _freqdist
from numpy.ma.core import mean
from numpy.lib.function_base import median, percentile
from palmyrweb.api.analysis import AnalysisQuery

def success(**kwargs):
    response = { "status":'success'}
    response.update(kwargs)
    return HttpResponse(json.dumps(response))

def error(message):
    
    return HttpResponse(json.dumps({ "status":"error" , "message":"%s" % str(message)}))


class FeatureTableCommand():
    ftname = None
    ftable = None
    ctx = None
    
    def __init__(self,ctx,ftname,ftable):
        self.ctx = ctx
        self.ftname = ftname
        self.ftable = ftable

    def set_target(self):
        if 'feature_name' in self.ctx.params:
            self.ftable.set_target(self.ctx.params['feature_name'])
            self.ctx.set_feature_table(self.ftname, self.ftable)
            return success()
        else:
            return error('No feature name defined')
        
    def reset_target(self):
            self.ftable.reset_target()
            self.ctx.set_feature_table(self.ftname, self.ftable)
            return success()

    def set_class(self):
        if 'feature_name' in self.ctx.params:
            is_class = self.ctx.params['is_class'] == 'true'
            fname = self.ctx.params['feature_name']
            feature = self.ftable.get_feature(fname)
            feature.set_class(is_class)
            self.ftable.set_feature(fname,feature)
            self.ctx.set_feature_table(self.ftname, self.ftable)
            return success()
        else:
            return error('No feature name defined')
        
        
    def _get_distribution_function(self,feature):
        df_dict = feature.freq_dist
            
        if feature.has_class():
            df = map(lambda (kv) : [kv[0],round(kv[1] * self.ftable.get_row_count(),3)],df_dict.items())
        else:
            
            df =  {
                    'categories' : df_dict.keys(),
                    'series' :  [{ 'name' : feature.name, 'data' : map(lambda (kv) : round(kv[1] * 100,3),df_dict.items()) }]
            }
        return df
    
    def get_distribution_function(self):
        if 'feature_name' in self.ctx.params:
            fname = self.ctx.params['feature_name']
            feature = self.ftable.get_feature(fname)
            
            return success(data=self._get_distribution_function(feature))
        else:
            return error('No feature name defined')

    def save(self):
        if 'filename' in self.ctx.params:
            filename = self.ctx.params['filename']
            self.ftable.save(get_user_root(self.ctx.request.user,ANALYSIS_ROOT)+os.sep +filename)
            return success(message="%s stored successfully" % filename) 
        else:
            self.ftable.save(get_user_root(self.ctx.request.user,ANALYSIS_ROOT)+os.sep + self.ctx.params['dpath'])
            return success(message="%s stored successfully" % self.ctx.params['dpath'])
    
    def use_feature(self):
        if 'feature_name' in self.ctx.params:
            if 'use_it' in self.ctx.params:
        
                self.ftable.use_feature(self.ctx.params['feature_name'],self.ctx.params['use_it']=='true')
                self.ctx.set_feature_table(self.ftname, self.ftable)
                return success()
            else:
                return error('No use_it param defined')
    
        else:
            return error('No feature name defined')
    
    def toggle_feature(self):
        if 'feature_name' in self.ctx.params:
            fname = self.ctx.params['feature_name']
            self.ftable.use_feature(fname,not self.ftable.get_feature(fname).is_usable())
            self.ctx.set_feature_table(self.ftname, self.ftable)
            return success(fname=fname,use=self.ftable.get_feature(fname).is_usable())
        else:
            return error('No feature name defined')
    
    def build_model(self):
        model,model_info = self.ftable.build_model()
        self.ftable.current_model = (model,model_info)
        self.ctx.set_feature_table(self.ftname, self.ftable)
        return success(model_info=model_info.get_properties())
        
    def save_model(self):
        if self.ftable.current_model is None:
            (model,model_info) = self.ftable.build_model()
        else:
            (model,model_info) = self.ftable.current_model
            
        model_name = model_info.name
        self.ftable.models[model_name] = (model,model_info)
        self.ctx.set_feature_table(self.ftname, self.ftable)

        return success()
    
    def add_feature(self):
        if 'name' not  in self.ctx.params:
            return error('No feature name defined')
        if 'type' not  in self.ctx.params:
            return error('No feature type defined')
        if 'code' not  in self.ctx.params:
            return error('No feature code defined')

        name = self.ctx.params['name']
        type = self.ctx.params['type']
        
        tc = TypeConverter()
        if not tc.is_supported_type(type):
            return error('%s type not supported' % type)
        
        code = self.ctx.params['code']
        self.ftable.add_feature(name,type,function_code=code)
        
        self.ctx.set_feature_table(self.ftname, self.ftable)

        return success(message="Virtual feature %s added successfully" % name )
    
    def get_feature(self):
        if 'name' not  in self.ctx.params:
            return error('No feature name defined')
        
        name = self.ctx.params['name']
        
        if not self.ftable.has_feature(name):
            return error("The feature %s doesn't exist")
        
        feature = self.ftable.get_feature(name)
        feature_data = {
                        'name' : feature.name,
                        'is_virtual' : feature.is_virtual(),
                        'virtual_feature_code' : feature.virtual_function_code,
                        'default_feature_code' : feature.default_function_code,
        }
        return success(feature=feature_data)
    
    def edit_feature(self):
        if 'name' not  in self.ctx.params:
            return error('No feature name defined')
        if 'virtual_function_code' not  in self.ctx.params:
            return error('No feature virtual function code defined')
        if 'default_function_code' not  in self.ctx.params:
            return error('No feature default function code defined')
        
        name = self.ctx.params['name']
        virtual_function_code = self.ctx.params['virtual_function_code'] 
        default_function_code = self.ctx.params['default_function_code']
        
        if not self.ftable.has_feature(name):
            return error("The feature %s doesn't exist")
        
        feature = self.ftable.get_feature(name)
        feature.virtual_function_code = virtual_function_code
        feature.default_function_code = default_function_code
        feature.update_feature()
        self.ctx.set_feature_table(self.ftname, self.ftable)
        
        return success(message="Feature %s successfully updated" % name)
     
    def remove_feature(self):
        if 'name' not  in self.ctx.params:
            return error('No feature name defined')
        name = self.ctx.params['name']
        
        if not self.ftable.has_feature(name):
            return error("The feature %s doesn't exist")
        
        self.ftable.remove_feature(name)
        
        self.ctx.set_feature_table(self.ftname, self.ftable)
        
        return success(message="Feature %s successfully removed" % name)
    
    def select_best_features(self):
        
        kbest = self.ftable.select_best_features()
        
        return success(kbest=kbest)
    
    def get_model_info(self):
        if 'name' not  in self.ctx.params:
            return error('No model name defined')
        name = self.ctx.params['name']
        
        if name not in self.ftable.models:
            return error('No model saved as %s' % name)
        
        model_info = self.ftable.models[name][1] #model info
        self.ftable.current_model = self.ftable.models[name]
        self.ftable.set_target(model_info.target)
        
        for (name,feature) in self.ftable.get_features():
            self.ftable.use_feature(name,name in model_info.selected_features)
        
        
        self.ctx.set_feature_table(self.ftname, self.ftable)
        
        return success(model_info=model_info.get_properties())
    
    def get_current_model_info(self):
        
        if self.ftable.current_model is None:
            return success(model_info=None)
        else:
            return success(model_info=self.ftable.current_model[1].get_properties())
        
    def apply_prediction(self):
        if 'model-name' not  in self.ctx.params:
            return error("model name not defined")
        if 'input' not  in self.ctx.params:
            return error("input filename not defined")
        if 'output' not  in self.ctx.params:
            return error("output filename not defined")
        model_name = self.ctx.params['model-name']
        input_filename = self.ctx.params['input']
        output_filename = self.ctx.params['output']
        
        self.ftable.apply_prediction(model_name,get_user_root(self.ctx.request.user,DATA_ROOT)+os.sep +input_filename,get_user_root(self.ctx.request.user,DATA_ROOT)+os.sep +output_filename)
        
        return success(message="Predictions saved to %s" % output_filename)
    
    
    
    def _correlate(self,fname_y,fname_x,options):
        #result = {}
        
        fx = self.ftable.get_feature(fname_x)
        fy = self.ftable.get_feature(fname_y)
        query = AnalysisQuery(fx,fy)
        
        if fx.has_class() or fx.get_type() == TEXT_TYPE:
            if fy.has_class(): #stacked bar
                               
                """
                series_x = fy.get_distribution_by(fx)
                    
                for category in fy.classes:
                    group_ids = self.ftable.get_row_ids()
                    group_values = fx.get_values(group_ids)
                    group_freq = _freqdist(group_values)
                    if '' in group_freq:
                        del group_freq['']
                    
                    serie = {
                             'name' : fy.name + "=" + unicode(int(category) if fy.get_type()==INT_TYPE else category),
                             'data' : map(lambda category : round(group_freq[category],4) if category in group_freq else 0 ,fx.classes)
                             }
                    series_y.append(serie)
                    
                
                
                flat_series = []
               
                for i in range(len(series_x)):
                   
                    for j in range(len(series_y)):
                        h =  series_x[i]['data'][j]
                        w =  series_y[j]['data'][i]
                       
                        flat_series.append({'w':w,'h':h})
                
                result['series'] = flat_series
                """
                
                return 'stacked-bar',query.query_as_stacked_bar()
            elif fy.get_type() == INT_TYPE or fy.get_type() == FLOAT_TYPE: #box plot
                return 'box-plot',query.query_as_box_plot()
            elif fy.get_type() == TEXT_TYPE :  #stacked bar
                return 'stacked-bar',query.query_as_stacked_bar()
            else:
                return None,None
    
        else:
            if (fx.get_type() == INT_TYPE or fx.get_type() == FLOAT_TYPE) and (fy.get_type() == INT_TYPE or fy.get_type() == FLOAT_TYPE):
                return 'scatter',query.query_as_scatter_plot()
            
            else:
                return None,None
    
    def nl_query(self):
        if 'query' not  in self.ctx.params:
            query = ""
        else:
            query = self.ctx.params['query']
        
        feature_y, feature_x, options = nlq_parse(query,self.ftable.get_feature_names())
        
        result_type = None
        data = None
        
        
        if feature_y is not None and feature_x is None: #single feature analysis
            feature = self.ftable.get_feature(feature_y)
            data = self._get_distribution_function(feature)
            
            if feature.has_class():
                result_type = 'pie'
            elif feature.get_type() == TEXT_TYPE:
                result_type = 'wordcloud'
            else:
                result_type = 'bar'
        elif feature_y is not None and feature_x is not None: #two features analysis
            
            type,data = self._correlate(feature_y,feature_x,options)
            result_type = type
        else: #show all
            result_type = 'table'
            if 'num_page' in options:
                num_page = int(options['num_page'])
            else:
                num_page = 0
            data = self.ftable.get_datatable(from_page=num_page)
        return success(type=result_type,data=data,query=query)
        
    