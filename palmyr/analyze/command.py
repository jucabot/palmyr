
from django.http import HttpResponse
from settings import CONTEXT
import os
from palmyrdb.converter import TEXT_TYPE, TypeConverter
from query.nlquery import nlq_parse
from query.analysis import AnalysisQuery, FeatureQuery
from pickle import dump
from palmyrdb.script import compile_func_code
from api.datahub import Datahub
from django.core.cache import cache
from api.command import Command, success

class FeatureTableCommand(Command):
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
            return self.success()
        else:
            return self.error('No feature name defined')
        
    def reset_target(self):
            self.ftable.reset_target()
            self.ctx.set_feature_table(self.ftname, self.ftable)
            return self.success()

    def set_class(self):
        if 'feature_name' in self.ctx.params:
            is_class = self.ctx.params['is_class'] == 'true'
            fname = self.ctx.params['feature_name']
            feature = self.ftable.get_feature(fname)
            feature.set_class(is_class)
            self.ftable.set_feature(fname,feature)
            self.ctx.set_feature_table(self.ftname, self.ftable)
            return self.success()
        else:
            return self.error('No feature name defined')
        
    def get_distribution_function(self):
        if 'feature_name' in self.ctx.params:
            fname = self.ctx.params['feature_name']
            feature = self.ftable.get_feature(fname)
            fq = FeatureQuery(feature)
            return self.success(data=fq.get_frequency_distribution())
        else:
            return self.error('No feature name defined')

        
    def save(self):
        if 'filename' in self.ctx.params:
            filename = self.ctx.params['filename']
            file_path = self.ctx.get_user_root(base=CONTEXT['analysis-root'])+os.sep +filename
            
            dir_path = file_path.split(os.sep)[:-1]
            dir_path = os.sep.join(dir_path)
        
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            f = open(file_path,'wb')
            dump(self.ftable,f)
            f.close()
            
            return self.success(message="%s enregistr&eacute; avec succ&egrave;s" % filename) 
        else:
            self.ftable.save(self.ctx.get_user_root(base=CONTEXT['analysis-root'])+os.sep + self.ctx.params['dpath'])
            return self.success(message="%s enregistr&eacute; avec succ&egrave;s" % self.ctx.params['dpath'])
    
    def use_feature(self):
        if 'feature_name' in self.ctx.params:
            if 'use_it' in self.ctx.params:
                self.ftable.use_feature(self.ctx.params['feature_name'],self.ctx.params['use_it']=='true')
                self.ctx.set_feature_table(self.ftname, self.ftable)
                return self.success()
            else:
                return self.error('No use_it param defined')
        else:
            return self.error('No feature name defined')
    
    def toggle_feature(self):
        if 'feature_name' in self.ctx.params:
            fname = self.ctx.params['feature_name']
            self.ftable.use_feature(fname,not self.ftable.get_feature(fname).is_usable())
            self.ctx.set_feature_table(self.ftname, self.ftable)
            return self.success(fname=fname,use=self.ftable.get_feature(fname).is_usable())
        else:
            return self.error('No feature name defined')
    
        
    def save_model(self):
        if self.ftable.current_model is None:
            (model,model_info) = self.ftable.build_model()
        else:
            (model,model_info) = self.ftable.current_model
            
        model_name = model_info.name
        self.ftable.models[model_name] = (model,model_info)
        self.ctx.set_feature_table(self.ftname, self.ftable)

        return self.success()
    
    def add_feature(self):
        if 'name' not  in self.ctx.params:
            return self.error('No feature name defined')
        if 'type' not  in self.ctx.params:
            return self.error('No feature type defined')
        if 'code' not  in self.ctx.params:
            return self.error('No feature code defined')

        name = self.ctx.params['name']
        type_name = self.ctx.params['type']
        
        tc = TypeConverter()
        if not tc.is_supported_type(type):
            return self.error('%s type not supported' % type_name)
        
        code = self.ctx.params['code']
        self.ftable.add_feature(name,type_name,function_code=code)
        
        self.ctx.set_feature_table(self.ftname, self.ftable)

        return self.success(message="Feature virtuelle %s ajout&eacute;e avec succ&egraves" % name )
    
    def get_feature(self):
        if 'name' not  in self.ctx.params:
            return self.error('No feature name defined')
        
        name = self.ctx.params['name']
        
        if not self.ftable.has_feature(name):
            return self.error("The feature %s doesn't exist")
        
        feature = self.ftable.get_feature(name)
        feature_data = {
                        'name' : feature.name,
                        'is_virtual' : feature.is_virtual(),
                        'virtual_feature_code' : feature.virtual_function_code,
                        'default_feature_code' : feature.default_function_code,
        }
        return self.success(feature=feature_data)
    
    def edit_feature(self):
        if 'name' not  in self.ctx.params:
            return self.error('No feature name defined')
        if 'virtual_function_code' not  in self.ctx.params:
            return self.error('No feature virtual function code defined')
        if 'default_function_code' not  in self.ctx.params:
            return self.error('No feature default function code defined')
        
        name = self.ctx.params['name']
        virtual_function_code = self.ctx.params['virtual_function_code'] 
        default_function_code = self.ctx.params['default_function_code']
        
        if not self.ftable.has_feature(name):
            return self.error("The feature %s doesn't exist")
        
        feature = self.ftable.get_feature(name)
        feature.virtual_function_code = virtual_function_code
        feature.default_function_code = default_function_code
        feature.update_feature()
        self.ctx.set_feature_table(self.ftname, self.ftable)
        
        return self.success(message="Feature %s mise a&agrave; jour avec succ&agrave;s" % name)
     
    def remove_feature(self):
        if 'name' not  in self.ctx.params:
            return self.error('No feature name defined')
        name = self.ctx.params['name']
        
        if not self.ftable.has_feature(name):
            return self.error("The feature %s doesn't exist")
        
        self.ftable.remove_feature(name)
        
        self.ctx.set_feature_table(self.ftname, self.ftable)
        
        return self.success(message="Feature %s supprim&eacute;e avec succ&grave;s" % name)
    
    def build_model(self):
        if 'filter' in self.ctx.params:
            filter_code = self.ctx.params['filter']
        else:
            filter_code = None
            
        if 'filter_name' in self.ctx.params:
            filter_name = self.ctx.params['filter_name']
        else:
            filter_name = None
            
        
        model,model_info = self.ftable.build_model(filter_name=filter_name,filter_code=filter_code)
        self.ftable.current_model = (model,model_info)
        self.ctx.set_feature_table(self.ftname, self.ftable)
        return self.success(model_info=model_info.get_properties())
    
    
    def select_best_features(self):
        if 'filter' in self.ctx.params:
            filter_code = self.ctx.params['filter']
        else:
            filter_code = None
        
        kbest = self.ftable.select_best_features(filter_code=filter_code)
        
        return self.success(kbest=kbest)
    
    def get_model_info(self):
        if 'name' not  in self.ctx.params:
            return self.error('No model name defined')
        name = self.ctx.params['name']
        
        if name not in self.ftable.models:
            return self.error('No model saved as %s' % name)
        
        model_info = self.ftable.models[name][1] #model info
        self.ftable.current_model = self.ftable.models[name]
        self.ftable.set_target(model_info.target)
        
        for (name,feature) in self.ftable.get_features():
            self.ftable.use_feature(name,name in model_info.selected_features)
        
        
        self.ctx.set_feature_table(self.ftname, self.ftable)
        
        return self.success(model_info=model_info.get_properties())
    
    def get_current_model_info(self):
        
        if self.ftable.current_model is None:
            return self.success(model_info=None)
        else:
            return self.success(model_info=self.ftable.current_model[1].get_properties())
        
    def apply_prediction(self):
        if 'model-name' not  in self.ctx.params:
            return self.error("model name not defined")
        if 'input' not  in self.ctx.params:
            return self.error("input filename not defined")
        if 'output' not  in self.ctx.params:
            return self.error("output filename not defined")
        model_name = self.ctx.params['model-name']
        input_filename = self.ctx.params['input']
        output_filename = self.ctx.params['output']
        
        self.ftable.apply_prediction(model_name,self.ctx.get_user_root()+os.sep +input_filename,self.ctx.get_user_root()+os.sep +output_filename)
        
        return self.success(message="Pr&eacute;dictions sauv&eacute;es dans %s" % output_filename)

    def _query(self,query):
        
        #check if cached
        cached_result = cache.get(self._get_cache_key())
        if cached_result is not None:
            return cached_result
        
        
        
        feature_y, feature_x, options = nlq_parse(query,self.ftable.get_feature_names())
        
        result_type = None
        data = None
        filter_function = None
        if 'filter'  in self.ctx.params:
            filter_code = self.ctx.params['filter']
            filter_function = compile_func_code(filter_code)
        
        if feature_y is not None and feature_x is None: #single feature analysis
            feature = self.ftable.get_feature(feature_y)
            fq = FeatureQuery(feature)
            fq.filter_function = filter_function
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
            analysis.filter_function = filter_function
            result_type,data = analysis.correlate()
            
        else: #search in datahub or show all
            
            result_type = 'table'
            if 'num_page' in options:
                num_page = int(options['num_page'])
            else:
                num_page = 0
            data = self.ftable.get_datatable(from_page=num_page,filter_function=filter_function)

        
        cache.set(self._get_cache_key(),(result_type,data),60*60*24*10)
        return (result_type,data)
    
    
    def _get_cache_key(self):
        def string_to_int(s):
            ord3 = lambda x : '%.3d' % ord(x)
            return int(''.join(map(ord3, s)))
                
        if 'filter' in self.ctx.params:
            cache_key = "%s|%s|%s|%s" % (self.ctx.user.id,string_to_int(self.ctx.params['ftable']),string_to_int(self.ctx.params['query']),string_to_int(self.ctx.params['filter']))
        else:
            cache_key = "%s|%s|%s" % (self.ctx.user.id,string_to_int(self.ctx.params['ftable']),string_to_int(self.ctx.params['query']))
        return cache_key
        
    
    def nl_query(self):
        if 'query' not  in self.ctx.params:
            query = ""
        else:
            query = self.ctx.params['query']
        
        (result_type,data) = self._query(query)
        
        return self.success(type=result_type,data=data,query=query)
    
    def add_filter(self):
        if 'name' not  in self.ctx.params:
            return self.error('No name defined')
        if 'code' not  in self.ctx.params:
            return self.error('No filter code defined')

        name = self.ctx.params['name']
        code = self.ctx.params['code']
        
        self.ftable.add_filter(name,code)
        
        self.ctx.set_feature_table(self.ftname, self.ftable)

        return self.success(message="Filtre %s cr&eacute;&eacute; avec succ&egrave;s" % name )
    def select_filter(self):
        if 'name' not  in self.ctx.params:
            return self.error('No name defined')
        
        name = self.ctx.params['name']
        
        if name not  in self.ftable.filters:
            return self.error('Filter %s doesn\'t exist' % name)

        filter_name = self.ftable.filters[name]
        
        self.ftable.current_filter = filter_name
        
        self.ctx.set_feature_table(self.ftname, self.ftable)

        return self.success(data=filter_name )
    def clear_filter(self):
        
        self.ftable.current_filter = None
        
        self.ctx.set_feature_table(self.ftname, self.ftable)

        return self.success()
    def remove_filter(self):
        
        name = self.ctx.params['name']
        
        if name not  in self.ftable.filters:
            return self.error('Filter %s doesn\'t exist' % name)

        del self.ftable.filters[name]
                
        self.ctx.set_feature_table(self.ftname, self.ftable)

        return self.success()
    
    def get_featureset(self):
        return success(data=self.ftable.get_properties())
    
    def remove_model(self):
        if 'model' not  in self.ctx.params:
            return self.error('No model name defined')
        model_name = self.ctx.params['model']
        del self.ftable.models[model_name]
        
        self.ctx.set_feature_table(self.ftname, self.ftable)

        return self.success()
    
    
    def index_query(self):
        if 'query' not  in self.ctx.params:
            return self.error('No query defined')
        else:
            query = self.ctx.params['query']
        
        (result_type,data) = self._query(query)
        
        datahub = Datahub(CONTEXT,user_id=self.ctx.user.id)
        serie_description = "%s dans %s" % (query,self.ftname)
        
        
        id_index = datahub.index(query,result_type,data, description=serie_description)
        
        return self.success(id=id_index)
        
    
    