from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def breadcrumb(value,arg="/"):
    i=0
    parts = []
    
    value = value.replace('//','/')
    
    if value[-1] == "/":
        value = value[:-1] 
    
    paths = value.split(arg)
    
    for i in range(len(paths)):
        parts.append((paths[i],build_part(i,paths,arg)))
    
    return mark_safe(render(parts))
    
def build_part(index, paths,sep):
    long_path = ""
    
    if index == 0:
        return sep
    for i in range(index+1):
        long_path += paths[i] + sep
    
    return long_path[:-1]


def render(parts):
        
    html = "<ul class=\"breadcrumb\">"
    for name,path in parts[:-1]:
        name = name if name != '' else "Mon dossier"
        html += "<li><a href=\"?path=" + path + "\">" + name + "</a> <span class=\"divider\">/</span></li>"
    name,path = parts[-1]
    name = name if name != '' else "Mon dossier"
    html += "<li class=\"active\">" + name  + "</li>"
    html += "</ul>"
    
    return html

