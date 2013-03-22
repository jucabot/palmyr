from palmyrdb.converter import INT_TYPE, NONE_VALUE, TEXT_TYPE, FLOAT_TYPE


class FeatureQuery():
    feature = None
    filter_function = None
    
    def __init__(self,feature,filter_function=None):
        self.feature = feature
        self.filter_function = filter_function
        
    def get_frequency_distribution(self):
        df_dict = self.feature.get_frequency_distribution(filter_function=self.filter_function)
            
        if self.feature.has_class():
            df = map(lambda (kv) : [kv[0],kv[1]],df_dict.items())
        else:
            
            df =  {
                    'categories' : df_dict.keys(),
                    'series' :  [{ 'name' : self.feature.name, 'data' : df_dict.values() }]
            }
        return df


class AnalysisQuery():
    fx = None
    fy = None
    filter_function=None
    
    def __init__(self,fx,fy,filter_function=None):
        self.fx = fx
        self.fy = fy
        self.filter_function = filter_function
    
    def query_as_stacked_bar(self):
        result = {}
        
        result['label_x'] = self.fx.name
        result['label_y'] = self.fy.name
        result['categories'] = map(lambda category : self.fx.name + "=" + unicode(int(category) if self.fx.get_type()==INT_TYPE else category),self.fx.classes)      
        result['series'] = self.fx.get_distribution_by(self.fy,centile=True,filter_function=self.filter_function)
        
        return result
    
    def query_as_box_plot(self):
        result = {}
                       
        result['label_x'] =  self.fx.name
        result['label_y'] =  self.fy.name
        result['categories'] =  self.fx.classes
        result['series'] = self.fy.get_distribution_stats_by( self.fx,centile=True,filter_function=self.filter_function)
        
        return result
    
    def query_as_scatter_plot(self):
        result = {}
        
        result['label_x'] = self.fx.name
        result['label_y'] = self.fy.name
        result['series'] = [{
                            'name' : self.fx.name + '^' + self.fy.name,
                            'data' : self.fx.get_correlation_with(self.fy,filter_function=self.filter_function)
                            }]
        return result
    
    def correlate(self):
       
        if self.fx.has_class() or self.fx.get_type() == TEXT_TYPE:
            if self.fy.has_class(): #stacked bar
                return 'stacked-bar',self.query_as_stacked_bar()
            elif self.fy.get_type() == INT_TYPE or self.fy.get_type() == FLOAT_TYPE: #box plot
                return 'box-plot',self.query_as_box_plot()
            elif self.fy.get_type() == TEXT_TYPE :  #stacked bar
                return 'stacked-bar',self.query_as_stacked_bar()
            else:
                return None,None
        else:
            if (self.fx.get_type() == INT_TYPE or self.fx.get_type() == FLOAT_TYPE) and (self.fy.get_type() == INT_TYPE or self.fy.get_type() == FLOAT_TYPE):
                return 'scatter',self.query_as_scatter_plot()
            
            else:
                return None,None