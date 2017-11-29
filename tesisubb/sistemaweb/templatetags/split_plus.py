
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


#
# @stringfilter
# @register.filter(name='split')
# def split_custom(string, sep):
#     return string.split(sep)

@register.filter(name='split_plus')
def split_plus(diccionario, index):



    for x in diccionario:
        for y,c in zip(x.keys(), x.values()):
            if y == index:
                print("ESOTY EN INDEX")
                return(c)





