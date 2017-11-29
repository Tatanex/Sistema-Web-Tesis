from lxml import etree

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


#
# @stringfilter
# @register.filter(name='split')
# def split_custom(string, sep):
#     return string.split(sep)

@register.filter(name='get_material')
def get_material(value):
   patron = value.split ('_')
   if( (len((patron)) <= 1)):

      return value

   else:



      source = 'media/data_materiales1.xml'
      doc = etree.parse (source)
      raiz = doc.getroot ()
      materiales = doc.findall ("Material")
      diccionario_materiales = {}
      for m in materiales:
         diccionario_materiales[m.attrib['Id']] = m.attrib['Name']

      if (patron[1] == 'RVAL'):
          return value
      else:


         if (patron[2] in diccionario_materiales) == True:

            return diccionario_materiales[patron[2]]
         else:
            return -500

