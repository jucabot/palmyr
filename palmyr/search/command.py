from api.command import Command
from settings import CONTEXT
from api.datahub import Datahub
from string import lower
from search.models import Workspace
from api.correlation import CorrelationSearch
import datetime

class SearchCommand(Command):
    
    def _query(self,query,user_id):
        
        datahub = Datahub(CONTEXT,user_id=user_id)
            
        result = datahub.get(query,"serie")
        
        if result is not None:
            result_type = result['display']
            data = result['data']
            data['description'] = result['description']
            data['source'] = result['source']
            data['zone'] = result['zone']
            data['id'] = query
            data['name'] = result['name']
            
        else:
            result = datahub.query(query)
            if result is not None: #the query match a datahub entry
                
                if len(result) == 1:
                    id = result[0][0]
                    result = result[0][1]
                    result_type = result['display']
                    data = result['data']
                    data['description'] = result['description']
                    data['source'] = result['source']
                    data['zone'] = result['zone']
                    data['name'] = result['name']
                    data['id'] = id
                else:
                                    
                    multi_timelines = len(result) <= 5
                    if multi_timelines:
                        for (id,serie) in result:
                            if serie['display'] != 'timeline':
                                multi_timelines = False
                                break
                    
                    if multi_timelines:
                        series = []
                        result_type = "timeline" #force to timeline
                                                                 
                        data = { "series" : map(lambda (id,item) : item['data']['series'][0] ,result) }                        
                    else:
                        data = result
                        result_type = 'serie-list'
            else:
                data = []
                result_type = 'serie-list'
        
        return (result_type,data)
        
    
    def search(self):
        
        query = self.ctx.params['query']
        
        (result_type,data) = self._query(query, self.ctx.request.user.id)
        
        return self.success(type=result_type,data=data,query=query)
    
    def correlate(self):
        
        query = self.ctx.params['query']
        (result_type, search_timeserie) = self._query(query, self.ctx.request.user.id)
        
        start = datetime.datetime.now()
        cs = CorrelationSearch(CONTEXT)
        result = cs.search(search_timeserie['series'][0]['data'])
        cs.close()
        
        return self.success(data=result,took=str(datetime.datetime.now()-start))
    
    
    def get_workspaces(self):
        workspaces = []
        if self.ctx.request.user.is_authenticated():
            workspace_set = self.ctx.request.user.workspace_set.all()
            for workspace in workspace_set:
                workspaces.append({'id':workspace.id,'name':workspace.name, 'value':workspace.value,'icon_path':workspace.icon_path })
        return self.success(workspaces=workspaces)
    
    def open_workspace(self):
        
        serie_id = self.ctx.params['id']
        name = self.ctx.params['name']
        
        (result_type,data) = self._query(serie_id, self.ctx.request.user.id)
        
        try:
            workspace = Workspace.objects.get(value=serie_id,user=self.ctx.request.user)
        except Workspace.DoesNotExist:
            workspace = Workspace(name=name,user=self.ctx.request.user,value=serie_id)
            workspace.save()
        
        return self.success(id=serie_id,name=name,data=data)
    
    def remove_workspace(self):
        
        id_workspace = self.ctx.params['id']
        
        try:
            workspace = Workspace.objects.get(id=id_workspace,user=self.ctx.request.user)
            workspace.delete()
        except Workspace.DoesNotExist:
            pass
        return self.success()
        