
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


#
# @stringfilter
# @register.filter(name='split')
# def split_custom(string, sep):
#     return string.split(sep)

@register.filter(name='get_key')
def get_key(diccionario, key):

   return (str(diccionario[key]))
