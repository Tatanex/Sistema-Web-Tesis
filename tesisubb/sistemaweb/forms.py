from django import forms
from django.forms import TextInput, Select, FileInput, CheckboxInput

from .models import Simular, Comparar, Modificar, Material, Combinar


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
        widgets = {
            'comparar_archivo_idf1': FileInput(attrs={'class': "form-control", 'id': "comparar_archivo_idf1"}),
            'comparar_archivo_idf2': FileInput(attrs={'class': "form-control", 'id': 'comparar_archivo_idf2'}),
        }

class ModificarIdfsForm(forms.ModelForm):
    class Meta:
        model = Modificar
        fields = ['modificar_id',
                  'modificar_archivo_idf']
        widgets = {
            'modificar_archivo_idf': FileInput(attrs={'class': "form-control",'id' : "modificar_archivo_idf" }),
        }


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['material_id',
                  'material_name',
                  'material_dsb_name',
                  'material_type']
        widgets = {
            'material_name': TextInput(attrs={'class': 'form-control'}),
            'material_dsb_name': TextInput(attrs={'class': "form-control"}),
            'material_type': Select(attrs={'class': 'form-control'}),
        }






class CombinarForm(forms.ModelForm):
    class Meta:
        model = Combinar
        fields = ['combinar_id',
                  'combinar_alternativas',
                 ]

