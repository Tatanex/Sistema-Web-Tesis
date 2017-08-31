from django import forms
from .models import Simular

class CargarArchivosForm(forms.ModelForm):
    class Meta:
        model = Simular
        fields = ['simular_id',
                  'simular_clima',
                  'simular_archivo_idf']