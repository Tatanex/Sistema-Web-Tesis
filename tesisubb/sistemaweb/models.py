# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
# Create your models here.
from django.urls import reverse
from django.core.management.base import BaseCommand
from subprocess import Popen
from django.utils.encoding import python_2_unicode_compatible, force_bytes

from .validators import validacion_extension_epw, validacion_extension_idf



class Simular(models.Model):
    simular_id = models.AutoField(primary_key=True)
    simular_clima = models.FileField(upload_to='epw/', validators=[validacion_extension_epw])
    simular_archivo_idf = models.FileField(upload_to='idf/', validators=[validacion_extension_idf])

    # def __unicode__(self):  # __unicode__ on Python 2
    #     return self.simular_id
    #
    def __unicode__(self):
        return str (self)

        # def __get_absolute_url__(self):
        #     return reverse('simular:detail', kwargs={ "id":self.simular_id })
        #


class Comparar(models.Model):
    comparar_id = models.AutoField(primary_key=True)
    comparar_archivo_idf1 = models.FileField(upload_to='comparacion_idf/', validators=[validacion_extension_idf])
    comparar_archivo_idf2 = models.FileField(upload_to='comparacion_idf/', validators=[validacion_extension_idf])


    def __unicode__(self):
        return str(self)





class Modificar(models.Model):
    modificar_id = models.AutoField(primary_key=True)
    modificar_archivo_idf = models.FileField(upload_to='modificacion_idf/', validators=[validacion_extension_idf])

    def __unicode__(self):
        return str(self)


    def __str__(self):
        return force_bytes (self)


class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    material_name = models.CharField (max_length=150)
    material_dsb_name = models.CharField (max_length=140)
    MATERIAL_TYPES = (
        ('MA', 'MATERIAL'),
        ('NO', 'MATERIAL_NOMASS'),
        ('GL', 'WINDOWS_MATERIAL_GLAZING'),
        ('GA', 'WINDOWS_MATERIAL_GAS'),
    )
    material_type = models.CharField (max_length=2, choices=MATERIAL_TYPES)


    def __unicode__(self):
        return str(self)


    def __str__(self):
        return force_bytes (self)



class Combinar(models.Model):
    combinar_id = models.AutoField(primary_key=True)
    combinar_alternativas = models.CharField(max_length=30)



    def __unicode__(self):
        return str(self)


    def __str__(self):
        return force_bytes (self)

