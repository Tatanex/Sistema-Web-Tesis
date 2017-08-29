from django import forms
from .models import Simular

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Simular
        fields = ['simular_id','simular_clima','simular_archivo_idf']