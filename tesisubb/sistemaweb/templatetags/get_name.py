
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


#
# @stringfilter
# @register.filter(name='split')
# def split_custom(string, sep):
#     return string.split(sep)

@register.filter(name='get_name')
def get_name(value):
    nombre = []
    patron = value.split ('_')
    if (len(patron) < 2):
        return (value)
    else:
        str1 = ' '.join (str (e) for e in patron)



        return (str(str1))


