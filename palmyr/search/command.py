from common.command import Command
from settings import CONTEXT
from common.datahub import Datahub
from string import lower
from search.models import Workspace
from common.correlation import CorrelationSearch
import datetime
import cjson

class SearchCommand(Command):
    

    def _query(self,query,user_id,es_from=0):
        total=0
        took = 0
        datahub = Datahub(CONTEXT,user_id=user_id)
            
        result = datahub.get(query)
        
        if result is not None:
            result_type = result['display']
            data = result['data']
            data['description'] = result['description']
            data['source'] = result['source']
            data['zone'] = result['zone']
            data['id'] = query
            data['name'] = result['name']
            
        else:
            result,total,took = datahub.query(query,es_from=es_from)
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
        
        return (result_type,data,total,took)
        
    
    def search(self):
        
        query = self.ctx.params['query']
        es_from = 0
        if 'from' in self.ctx.params:
            es_from = int(self.ctx.params['from'])
        
        (result_type,data,total,took) = self._query(query, self.ctx.request.user.id,es_from=es_from)
        
        return self.success(type=result_type,data=data,query=query,total=total,took=took,es_from=es_from)
    
    def correlate(self):
        
        query = self.ctx.params['query']
        (result_type, search_timeserie,total,took) = self._query(query, self.ctx.request.user.id)
        
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
                workspaces.append({'id':workspace.id,'name':workspace.name, 'serie_id':workspace.serie_id,'icon_path':workspace.icon_path,'options':workspace.options })
        return self.success(workspaces=workspaces)
    
    def open_workspace(self):
        
        serie_id = self.ctx.params['id']
        name = self.ctx.params['name']
        
        (result_type,data,total,took) = self._query(serie_id, self.ctx.request.user.id)
        
        try:
            workspace = Workspace.objects.get(serie_id=serie_id,user=self.ctx.request.user)
        except Workspace.DoesNotExist:
            workspace = Workspace(name=name,user=self.ctx.request.user,serie_id=serie_id)
            workspace.save()
        
        return self.success(id=serie_id,name=name,data=data,options=cjson.decode(workspace.options))
    
    def remove_workspace(self):
        
        id_workspace = self.ctx.params['id']
        
        try:
            workspace = Workspace.objects.get(id=id_workspace,user=self.ctx.request.user)
            workspace.delete()
            
            #todo supprimer de l'index si donnees privees
            
            
        except Workspace.DoesNotExist:
            return self.error(message="Espace de travail %s inexistant" % id_workspace)
        return self.success()
        
