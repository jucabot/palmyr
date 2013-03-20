from django.http import HttpResponse
import json
from web.views import get_user_root
from settings import CONTEXT
import os
from palmyrdb.converter import TEXT_TYPE, TypeConverter
from web.api.nlquery import nlq_parse
from web.api.analysis import AnalysisQuery, FeatureQuery
from pickle import dump

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
        
    def get_distribution_function(self):
        if 'feature_name' in self.ctx.params:
            fname = self.ctx.params['feature_name']
            feature = self.ftable.get_feature(fname)
            fq = FeatureQuery(feature)
            return success(data=fq.get_frequency_distribution())
        else:
            return error('No feature name defined')

        
    def save(self):
        if 'filename' in self.ctx.params:
            filename = self.ctx.params['filename']
            file_path = get_user_root(self.ctx.request.user,CONTEXT['analysis-root'])+os.sep +filename
            
            dir_path = file_path.split(os.sep)[:-1]
            dir_path = os.sep.join(dir_path)
        
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            f = open(file_path,'wb')
            dump(self.ftable,f)
            f.close()
            
            return success(message="%s stored successfully" % filename) 
        else:
            self.ftable.save(get_user_root(self.ctx.request.user,CONTEXT['analysis-root'])+os.sep + self.ctx.params['dpath'])
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
        
        self.ftable.apply_prediction(model_name,get_user_root(self.ctx.request.user,CONTEXT['data-root'])+os.sep +input_filename,get_user_root(self.ctx.request.user,CONTEXT['data-root'])+os.sep +output_filename)
        
        return success(message="Predictions saved to %s" % output_filename)
    
    
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
            fq = FeatureQuery(feature)
            data = fq.get_frequency_distribution()
            
            if feature.has_class():
                result_type = 'pie'
            elif feature.get_type() == TEXT_TYPE:
                result_type = 'wordcloud'
            else:
                result_type = 'bar'
        elif feature_y is not None and feature_x is not None: #two features analysis
            fx = self.ftable.get_feature(feature_x)
            fy = self.ftable.get_feature(feature_y)
            analysis = AnalysisQuery(fx,fy)
            result_type,data = analysis.correlate()
            
        else: #show all
            result_type = 'table'
            if 'num_page' in options:
                num_page = int(options['num_page'])
            else:
                num_page = 0
            data = self.ftable.get_datatable(from_page=num_page)
        return success(type=result_type,data=data,query=query)
        
    