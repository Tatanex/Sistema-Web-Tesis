from django import forms
from django.forms import TextInput, Select, FileInput

from .models import Simular, Comparar, Modificar, Materials


class CargarArchivosForm(forms.ModelForm):
    class Meta:
        model = Simular
        fields = ['simular_id',
                  'simular_clima',
                  'simular_archivo_idf']
        widgets = {
            'simular_clima': FileInput(attrs={'class': "form-control",'id' : "simular_clima" }),
            'simular_archivo_idf': FileInput(attrs={'class': "form-control",'id' : 'simular_idf'}),
        }

class CompararIdfsForm(forms.ModelForm):
    class Meta:
        model = Comparar
        fields = ['comparar_id',
                  'comparar_archivo_idf1',
                  'comparar_archivo_idf2']

class ModificarIdfsForm(forms.ModelForm):
    class Meta:
        model = Modificar
        fields = ['modificar_id',
                  'modificar_archivo_idf']
        widgets = {
            'modificar_archivo_idf': FileInput(attrs={'class': "form-control",'id' : "modificar_archivo_idf" }),
        }


class MaterialsForm(forms.ModelForm):
    class Meta:
        model = Materials
        fields = ['materials_id',
                  'materials_name',
                  'materials_dsb_name',
                  'materials_type']
        widgets = {
            'materials_name': TextInput(attrs={'class': 'form-control'}),
            'materials_dsb_name': TextInput(attrs={'class': "form-control"}),
            'materials_type': Select(attrs={'class': 'form-control'}),
        }

