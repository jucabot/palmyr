from common.context import UserContext
from common.command import Command
from django.contrib.auth.decorators import login_required
import traceback
from common.forms import UploadFileForm
import os
from django.core.cache import cache
from os.path import isfile,isdir, join
from os import listdir

def get_path(request):
    path = "/"
    if 'path' in request.GET:
        path = request.GET['path'].replace('.','/')
    if path == '':
        path = "/"
    return path

@login_required
def api(request):
    
    cmd_op = request.GET['cmd']
    ctx = UserContext(request)
    cmd = Command(ctx)
    try:
        
        if cmd_op == 'clear-cache':
            cache.clear()
            return cmd.success(message="Cache cleared")
        elif cmd_op == 'list-data-files':
            user_dir = ctx.get_user_root() + ctx.params['path']
            files = [ f for f in listdir(user_dir) if isfile(join(user_dir,f)) ]
            dirs = [ f for f in listdir(user_dir) if isdir(join(user_dir,f)) ]
            
            return cmd.success(files=files,directories=dirs)
            
        elif cmd_op == 'upload-file':
            if request.method == 'POST':
                form = UploadFileForm(request.POST, request.FILES)
                if form.is_valid():
                    
                    if request.FILES['file'].size > 500000: #max upload file
                        return cmd.error("la limite de taille est de 500ko")
                    
                    name = request.FILES['file'].name
                    user_dir = ctx.get_user_root() + get_path(request) if 'path' in ctx.params else ''
    
                    path =  user_dir + os.sep + name
                    destination = open(path, 'wb+')
                    for chunk in request.FILES['file'].chunks():
                        destination.write(chunk)
                    destination.close()
                    
                    return cmd.success(files=[{'name': name, 'path':path}])
                else:
                    return cmd.error("%s n'est pas un fichier .CSV" % request.FILES['file'].name )
            else:
                return cmd.error('GET operation not supported')
        else:
            return cmd.error('Undefined api command %s' % cmd_op)

    except Exception, e:
        print traceback.format_exc()
        return cmd.error(str(e))

 