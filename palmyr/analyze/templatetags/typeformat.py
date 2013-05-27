from django import template
from django.utils.safestring import mark_safe
from analyze.featuredb.converter import TEXT_TYPE, INT_TYPE, FLOAT_TYPE

register = template.Library()


@register.filter
def type_name(type,lang='en'):
    
    if type == TEXT_TYPE:
        return "Text"
    elif type == INT_TYPE or type == FLOAT_TYPE:
        return "Numeric"
    else:
        return type

@register.filter
def type_format(value,type_name,lang='en'):
    if type_name == INT_TYPE:
        return "%i" % value
    elif type_name == FLOAT_TYPE:
        if int(value) == float(value):
            return "%i" % round(value)
        else:
            return "%.2f" % round(value)
    else:
        return value