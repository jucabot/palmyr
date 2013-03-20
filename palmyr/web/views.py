# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from web.forms import UploadFileForm
from django.template.context import RequestContext
from settings import CONTEXT
import os
from os import listdir
from os.path import isfile,isdir, join,normpath
from palmyrdb.featureset import FeatureTable
from web.context import UserContext
from pickle import load

 

@login_required
def home(request):
    context = {'active_menu' : 'home' }
    return render_to_response('home.html',context)

#Data source

def get_user_root(user,root):
    user_dir = root + os.sep + str(user.id)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return normpath(user_dir)

def handle_uploaded_file(f,filename,user):
    user_dir = get_user_root(user,CONTEXT['data-root'])
    
    path =  user_dir + os.sep +filename
    destination = open(path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return path
    
@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            name = request.FILES['file'].name
            path = handle_uploaded_file(request.FILES['file'],name,request.user)
            #file_instance = FileDataSource(name=name.name,path=path)
            #file_instance.save()
            
        path, dirs,files = browse(request,CONTEXT['data-root'])
        
        context = {
            'active_menu' : 'datasource',
            'path': path,
            'upload_form' : form,
            'files' : files,
            'directories' : dirs,
        }
        return render_to_response('datasource/browse.html',context,context_instance=RequestContext(request))


def browse(request, ROOT):
    path = "/"
    if 'path' in request.GET:
        path = request.GET['path'].replace('.','/')
    if path == '':
        path = "/"
    
    user_dir = get_user_root(request.user, ROOT) + path
    files = [ f for f in listdir(user_dir) if isfile(join(user_dir,f)) ]
    dirs = [ f for f in listdir(user_dir) if isdir(join(user_dir,f)) ]

    return path, dirs,files

@login_required
def browse_datasource(request):
    form = UploadFileForm()
    
    path, dirs,files = browse(request,CONTEXT['data-root'])
    
    context = {
        'active_menu' : 'datasource',
        'path': path,
        'upload_form' : form,
        'files' : files,
        'directories' : dirs,
    }
    return render_to_response('datasource/browse.html',context,context_instance=RequestContext(request))

#Analysis
@login_required
def browse_analysis(request):
    
    path, dirs,files = browse(request,CONTEXT['analysis-root'])
    context = {
        'active_menu' : 'analysis',
        'path': path,
        'files' : files,
        'directories' : dirs,
    }
    return render_to_response('analysis/browse.html',context,context_instance=RequestContext(request))

"""
    Create an analysis from a file
    (long running)
"""
@login_required
def create_analysis(request):
    
    dpath = request.GET["dpath"]
    datasource_path = get_user_root(request.user,CONTEXT['data-root']) + dpath
    
    #Create feature table from dpath file
    ftable = FeatureTable(context=CONTEXT)
    ftable.load_from_csv(datasource_path)
    ftable.params['datasource-path'] = datasource_path
    name = dpath.split(os.sep)[-1]
    ftable.set_target(ftable.get_features()[0][0]) # define first feature as target
    
    #save feature table in session as user cache
    request.session['feature_tables:'+dpath] = ftable
    
    ftable.params['name'] = name #dpath name is default name
    
    context = {
        'active_menu' : 'analysis',
        'dpath': dpath,
        'name' : name,
        'ftable' : ftable,
        'tab' : 'summary',
        
    }
    
    return render_to_response('analysis/summary.html',context,context_instance=RequestContext(request))

@login_required
def open_analysis(request):
    
    dpath = request.GET["dpath"]
    analysis_path = get_user_root(request.user,CONTEXT['analysis-root']) + dpath
    
    #Create feature table from dpath file
    f = open(analysis_path,'rb')
    ftable = load(f)
    f.close()

    #save feature table in session as user cache
    request.session['feature_tables:'+dpath] = ftable
    
    name = dpath.split(os.sep)[-1]
    
    context = {
        'active_menu' : 'analysis',
        'dpath': dpath,
        'name' : name,
        'ftable' : ftable,
        'tab' : 'correlate',
        
    }
    
    return render_to_response('analysis/correlate.html',context,context_instance=RequestContext(request))


@login_required
def summary_analysis(request):
    
    if 'dpath' in request.GET:
        dpath = request.GET["dpath"]
        
        if 'feature_tables:'+dpath in request.session:
            ftable = request.session['feature_tables:'+dpath]
        
            context = {
            'active_menu' : 'analysis',
            'dpath': dpath,
            'name' : dpath.split(os.sep)[-1],
            'ftable' : ftable,
            'features' : ftable.get_features(),
            'tab' : 'summary'
            
            }
            return render_to_response('analysis/summary.html',context,context_instance=RequestContext(request))
        else:
            return redirect('browse-analysis')
    else:
        return redirect('browse-analysis')


@login_required
def model_analysis(request):
    
    if 'dpath' in request.GET:
        dpath = request.GET["dpath"]
        
        if 'feature_tables:'+dpath in request.session:
            ftable = request.session['feature_tables:'+dpath]
        
            context = {
            'active_menu' : 'analysis',
            'dpath': dpath,
            'name' : dpath.split(os.sep)[-1],
            'ftable' : ftable,
            'features' : ftable.get_features(),
            'tab' : 'model'
            
            }
            return render_to_response('analysis/model.html',context,context_instance=RequestContext(request))
        else:
            return redirect('browse-analysis')
    else:
        return redirect('browse-analysis')
        
@login_required
def correlate_analysis(request):
    
    if 'dpath' in request.GET:
        dpath = request.GET["dpath"]
        
        if 'feature_tables:'+dpath in request.session:
            ftable = request.session['feature_tables:'+dpath]
        
            context = {
            'active_menu' : 'analysis',
            'dpath': dpath,
            'name' : dpath.split(os.sep)[-1],
            'ftable' : ftable,
            'features' : ftable.get_features(),
            'tab' : 'correlate'
            }
            return render_to_response('analysis/correlate.html',context,context_instance=RequestContext(request))
        else:
            return redirect('browse-analysis')
    else:
        return redirect('browse-analysis')
            
    

    
 
    
    
    
    