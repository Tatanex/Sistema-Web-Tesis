from django import forms
from .models import Simular, Comparar


class CargarArchivosForm(forms.ModelForm):
    class Meta:
        model = Simular
        fields = ['simular_id',
                  'simular_clima',
                  'simular_archivo_idf']


class CompararIdfsForm(forms.ModelForm):
    class Meta:
        model = Comparar
        fields = ['comparar_id',
                  'comparar_archivo_idf1',
                  'comparar_archivo_idf2']

class ModificarIdfsForm(forms.ModelForm):
    class Meta:
        model = Comparar
        fields = ['comparar_id',
                  'comparar_archivo_idf1',
                  'comparar_archivo_idf2']
