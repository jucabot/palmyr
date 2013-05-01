# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from settings import CONTEXT
from search.models import Domain
from django.contrib.auth.models import User
from web.context import UserContext
from search.command import SearchCommand
import traceback


def api(request):
    
    cmd_op = request.GET['cmd']
    ctx = UserContext(request)
    cmd = SearchCommand(ctx)
    try:
        
        if cmd_op == 'search':
            return cmd.search()
        elif cmd_op == 'get-workspaces':
            return cmd.get_workspaces()
        elif cmd_op == 'open-workspace':
            return cmd.open_workspace()
        elif cmd_op == 'remove-workspace':
            return cmd.remove_workspace()
        else:
            return cmd.error('Undefined api command %s' % cmd_op)

    except Exception, e:
        print traceback.format_exc()
        return cmd.error(str(e))

 
 
def search(request):
    
    domains = Domain.objects.all()
    if request.user.is_authenticated():
        workspaces = request.user.workspace_set.all()
    else:
        workspaces = [] 
    
    context = {
    'active_menu' : 'search',
    'domains' : domains,
    'workspaces' : workspaces,
    }
    return render_to_response('search/search.html',context,context_instance=RequestContext(request))

    
    
