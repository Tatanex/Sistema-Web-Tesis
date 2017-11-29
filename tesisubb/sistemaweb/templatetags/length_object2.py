from django import template
from django.template.defaultfilters import stringfilter

register = template.Library ()


@register.filter (name='length_object2')
def length_object2(diccionario_construcction, key):

    if key == '1001':

       return 2
    else:
        llave = int(key) + 1
        print (diccionario_construcction[llave])
        return(len(diccionario_construcction[llave].fieldvalues)-1)




