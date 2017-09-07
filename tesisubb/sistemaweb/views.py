# -*- coding: utf-8 -*-

import os

import shutil
from django.core.files.storage import FileSystemStorage
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.context import RequestContext
from django.views.generic.edit import FormView




# Create your views here.

# View Index
from subprocess import Popen



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

def submit(request, args):
    if request.method == 'POST':
        WeatherData = '/usr/local/EnergyPlus-8-7-0/WeatherData/'
        simulation = get_object_or_404 (Simular, pk=args)
        b =str(simulation.simular_clima)

        # shutil.move ("media/"+b, WeatherData )
        climapalabra =  b.split("/")
        print(climapalabra)
        clima = climapalabra[1]


        # if os.path.isfile('/usr/local/EnergyPlus-8-6-0/WeatherData/'+clima) == True:
        #     print("EXISTE ARCHIVO")
        # else:
        #     shutil.copy ('media/'+b, '/usr/local/EnergyPlus-8-6-0/WeatherData/')

        clima_oficial = WeatherData+clima
        a = 'media/'+str(simulation.simular_archivo_idf)
        # print(b)
        # print(a)
        nueva_carpeta = 'simulaciones/simulacion_' + str (args)
        print(nueva_carpeta)
        if not os.path.exists(nueva_carpeta): os.makedirs (nueva_carpeta)
        p = Popen(['/usr/local/EnergyPlus-8-6-0/runenergyplus',a, clima,'-d',nueva_carpeta,'-p',str(args)]).wait()

        shutil.move ("media/idf/Output", "simulaciones/simulacion_" + str (args))
    return  render(request,'simulando.html')

