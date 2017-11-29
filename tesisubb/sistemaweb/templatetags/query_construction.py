
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()



@register.filter(name='query_construction')
def query_construction(diccionario_construcction, key):
    if key in diccionario_construcction:
       return 2
    else:
       return 0



