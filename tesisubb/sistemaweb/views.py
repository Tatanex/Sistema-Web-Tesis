# -*- coding: utf-8 -*-

import os

from django.core.files.storage import FileSystemStorage
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.context import RequestContext
from django.views.generic.edit import FormView




# Create your views here.

# View Index
from .models import Simular


def indexView(request):
    return render (request, 'layout.html')


def simularView(request, simulacion_id):
    simulacion = get_object_or_404(Simular, pk=simulacion_id)
    return render (request, 'simular.html', {'simulacion': simulacion})


# HTTP Error 400
def error_404View(request):
    return render (request, 'page_404.html')

from .forms import CargarArchivosForm


def cargar_archivo_simulacion_view(request):

    if request.method == 'POST':
        form = CargarArchivosForm(request.POST, request.FILES)
        if form.is_valid():
            nueva_simulacion = form.save()
            simulacion =  get_object_or_404(Simular, pk=nueva_simulacion.pk )
            # message = "Archivos cargados satisfactoriamente !"
            return render (request, 'simular.html', {'simulacion': simulacion})
    else:
        form = CargarArchivosForm()

    return render(request, 'upload.html',locals(), {'form': form})


