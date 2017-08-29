# -*- coding: utf-8 -*-

import os

from django.core.files.storage import FileSystemStorage
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from django.template.context import RequestContext
from django.views.generic.edit import FormView




# Create your views here.

# View Index
from .models import Simular


def indexView(request):
    return render (request, 'layout.html')


def simularView(request):
    return render (request, 'simular.html')


# HTTP Error 400
def error_404View(request):
    return render (request, 'page_404.html')

from .forms import UploadFileForm


def upload_file_view(request):

    if request.method == 'POST':


        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            a = form.auto_id
            message = "Archivos cargados satisfactoriamente !"
            return redirect('simular.html', pk=a)
    else:
        form = UploadFileForm()

    return render(request, 'upload.html',locals(), {'form': form})