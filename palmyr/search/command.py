from api.command import Command
from settings import CONTEXT
from api.datahub import Datahub
from string import lower

class SearchCommand(Command):
    
    def search(self):
        
        query = self.ctx.params['query']
        
        datahub = Datahub(CONTEXT,user_id=self.ctx.request.user.id)
            
        result = datahub.get(lower(query),"serie")
        
        if result is not None:
            result_type = result['display']
            data = result['data']
        else:
            result = datahub.query(query)
            if result is not None: #the query match a datahub entry
                
                if len(result) == 1:
                    result_type = result[0]['display']
                    data = result[0]['data']
                else:
                                    
                    multi_timelines = len(result) <= 5
                    if multi_timelines:
                        for serie in result:
                            if serie['display'] != 'timeline':
                                multi_timelines = False
                                break
                    
                    if multi_timelines:
                        series = []
                        result_type = "timeline" #force to timeline
                                                                 
                        
                        data = { "series" : map(lambda item : item['data']['series'][0] ,result) }                        
                    else:
                        data = result
                        result_type = 'serie-list'
        
        return self.success(type=result_type,data=data,query=query)