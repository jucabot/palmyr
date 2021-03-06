from analyze.featuredb.converter import INT_TYPE, NONE_VALUE, TEXT_TYPE, FLOAT_TYPE,\
    DATE_TYPE


class FeatureQuery():
    feature = None
    filter_function = None
    
    
    def __init__(self,feature,filter_function=None):
        self.feature = feature
        self.filter_function = filter_function
        
    def get_frequency_distribution(self):
        df_dict = self.feature.get_frequency_distribution(filter_function=self.filter_function)
        
        df =  {
                    'categories' : sorted(df_dict.keys()),
                    'series' :  [{ 'name' : self.feature.name, 'data' : map(lambda (k,v):v,sorted(df_dict.items())) }]
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
        limit = 100
        result['label_x'] =  self.fx.name
        result['label_y'] =  self.fy.name
        result['categories'] =  self.fx.classes if len(self.fx.classes) < limit else self.fx.classes[:limit]
        series = self.fy.get_distribution_stats_by( self.fx,centile=True,filter_function=self.filter_function)
        result['series'] = series if len(series) < limit else series[:limit]
        return result
    
    def query_as_scatter_plot(self):
        result = {}
        limit = 10000
        result['label_x'] = self.fx.name
        result['label_y'] = self.fy.name
        data = self.fx.get_correlation_with(self.fy,filter_function=self.filter_function)
        result['series'] = [{
                            'name' : self.fx.name + '^' + self.fy.name,
                            'data' : data if len(data) < limit else data[:limit]
                            }]
        return result
    
    def query_as_timeline(self):
        result = {}
                       
        result['label_x'] =  self.fx.name
        result['label_y'] =  self.fy.name
        #result['categories'] =  self.fx.classes
        
        result['series'] = [{
                            'name' : self.fy.name,
                            'data' : self.fy.get_metric_by( self.fx,metric_function=sum,filter_function=self.filter_function)
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
        elif self.fx.get_type() == DATE_TYPE:
            if self.fy.has_class(): #stacked bar
                return 'stacked-bar',self.query_as_stacked_bar()
            elif self.fy.get_type() == INT_TYPE or self.fy.get_type() == FLOAT_TYPE: #box plot
                return 'timeline',self.query_as_timeline()
            
        
        else:
            if (self.fx.get_type() == INT_TYPE or self.fx.get_type() == FLOAT_TYPE) and (self.fy.get_type() == INT_TYPE or self.fy.get_type() == FLOAT_TYPE):
                return 'scatter',self.query_as_scatter_plot()
            
            else:
                return None,None