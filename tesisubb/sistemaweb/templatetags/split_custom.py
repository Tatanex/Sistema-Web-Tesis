
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


#
# @stringfilter
# @register.filter(name='split')
# def split_custom(string, sep):
#     return string.split(sep)

@register.filter(name='split')
def split(value):

    if(value == 'LinearBridgingLayer'):
        return (str (value))
    else:
        patron = value.split ('_')
        # patron[2]
        return (str(patron[2]))
