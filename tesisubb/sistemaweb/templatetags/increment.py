
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


#
# @stringfilter
# @register.filter(name='split')
# def split_custom(string, sep):
#     return string.split(sep)

@register.filter(name='increment')
def increment(List):
   List.pop(0)


   # print ("estoy en increment"+ str(List))

   return(List)

