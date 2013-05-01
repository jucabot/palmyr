from api.command import Command
from settings import CONTEXT
from api.datahub import Datahub
from string import lower
from search.models import Workspace

class SearchCommand(Command):
    
    def search(self):
        result_type = None
        data = None
        
        query = self.ctx.params['query']
        
        datahub = Datahub(CONTEXT,user_id=self.ctx.request.user.id)
            
        result = datahub.get(query,"serie")
        
        if result is not None:
            result_type = result['display']
            data = result['data']
            data['description'] = result['description']
            data['source'] = result['source']
            data['zone'] = result['zone']
        else:
            result = datahub.query(query)
            if result is not None: #the query match a datahub entry
                
                if len(result) == 1:
                    result_type = result[0]['display']
                    data = result[0]['data']
                    data['description'] = result[0]['description']
                    data['source'] = result[0]['source']
                    data['zone'] = result[0]['zone']
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
            else:
                data = []
                result_type = 'serie-list'
        return self.success(type=result_type,data=data,query=query)
    
    def get_workspaces(self):
        workspaces = []
        if self.ctx.request.user.is_authenticated():
            workspace_set = self.ctx.request.user.workspace_set.all()
            for workspace in workspace_set:
                workspaces.append({'id':workspace.id,'name':workspace.name, 'icon_path':workspace.icon_path })
        return self.success(workspaces=workspaces)
    
    def open_workspace(self):
        
        serie_id = self.ctx.params['serie_id']
        
        try:
            workspace = Workspace.objects.get(name=serie_id,user=self.ctx.request.user)
        except Workspace.DoesNotExist:
            workspace = Workspace(name=serie_id,user=self.ctx.request.user,value='{}')
            workspace.save()
        
        return self.success(name=serie_id)
    
    def remove_workspace(self):
        
        id_workspace = self.ctx.params['id']
        
        try:
            workspace = Workspace.objects.get(id=id_workspace,user=self.ctx.request.user)
            workspace.delete()
        except Workspace.DoesNotExist:
            pass
        return self.success()
        