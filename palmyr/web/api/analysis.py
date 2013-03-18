from palmyrdb.converter import INT_TYPE, NONE_VALUE

class AnalysisQuery():
    fx = None
    fy = None
    
    def __init__(self,fx,fy):
        self.fx = fx
        self.fy = fy
    
    def query_as_stacked_bar(self):
        result = {}
        
        result['label_x'] = self.fx.name
        result['label_y'] = self.fy.name
        result['categories'] = map(lambda category : self.fx.name + "=" + unicode(int(category) if self.fx.get_type()==INT_TYPE else category),self.fx.classes)      
        result['series'] = self.fx.get_distribution_by(self.fy,centile=True)
        
        return result
    
    def query_as_box_plot(self):
        result = {}
                       
        result['label_x'] =  self.fx.name
        result['label_y'] =  self.fy.name
        result['categories'] =  self.fx.classes
        result['series'] = self.fy.get_distribution_stats_by( self.fx,centile=True)
        
        return result
    
    def query_as_scatter_plot(self):
        result = {}
        exclude_none_value_function = lambda table,i : table.get_value(self.fx.name,i) != NONE_VALUE and table.get_value(self.fy.name,i) != NONE_VALUE
                
        result['label_x'] = self.fx.name
        result['label_y'] = self.fy.name
        result['series'] = [{
                            'name' : self.fx.name + '^' + self.fy.name,
                            'data' : self.fx.get_correlation_with(self.fy,filter_function=exclude_none_value_function)
                            }]
        return result