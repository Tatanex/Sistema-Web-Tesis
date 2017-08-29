from django.core.exceptions import ValidationError



def validacion_extension_idf(value):
    if (not value.name.endswith ('.idf')):
        raise ValidationError ("EN ARCHIVO IDF, SOLO SE PERMITE FICHEROS CON EXTENSION .idf")

def validacion_extension_epw(value):
    if (not value.name.endswith ('.epw')):
        raise ValidationError ("EN ARCHIVO CLIMA, SOLO SE PERMITE FICHEROS CON EXTENSION .epw")
