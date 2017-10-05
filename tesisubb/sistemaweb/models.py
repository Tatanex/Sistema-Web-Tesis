# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
# Create your models here.
from django.urls import reverse
from django.core.management.base import BaseCommand
from subprocess import Popen
from django.utils.encoding import python_2_unicode_compatible, force_bytes

from .validators import validacion_extension_epw, validacion_extension_idf


class Construccion(models.Model):
    construccion_id = models.AutoField(primary_key=True)
    construccion_outside = models.FloatField()
    construccion_layer2 = models.FloatField()
    construccion_layer3 = models.FloatField()
    construccion_layer4 = models.FloatField()

    def __unicode__(self): # __unicode__ on Python 2
        return self.construccion_id

class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    construccion_id = models.ForeignKey(Construccion)
    material_name = models.CharField(max_length=150)
    material_roughness = models.FloatField()
    material_thickness = models.FloatField()
    material_conductivity = models.FloatField()
    material_density = models.FloatField()
    material_specific_heat = models.FloatField()
    material_thermal_absorptance = models.FloatField()
    material_solar_absorptance = models.FloatField()

    def __unicode__(self):  # __unicode__ on Python 2
        return self

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


class ReporteSimulacion(models.Model):
    reporte_id = models.AutoField(primary_key=True)
    reporte_totalenergy_totalsite = models.FloatField()
    reporte_totalenergy_totalsource = models.FloatField()
    reporte_distric_heating_heating = models.FloatField()
    reporte_distric_time_etpoint = models.FloatField()
    reporte_heating_intensity_hvac = models.FloatField()

    def __unicode__(self):  # __unicode__ on Python 2
        return self.reporte_id




class Modificar(models.Model):
    modificar_id = models.AutoField(primary_key=True)
    modificar_archivo_idf = models.FileField(upload_to='modificacion_idf/', validators=[validacion_extension_idf])

    def __unicode__(self):
        return str(self)


    def __str__(self):
        return force_bytes (self)


class Materials(models.Model):
    materials_id = models.AutoField(primary_key=True)
    materials_name = models.CharField (max_length=150)
    materials_dsb_name = models.CharField (max_length=140)
    MATERIALS_TYPES = (
         ('MA', 'MATERIAL'),
         ('NO', 'MATERIAL_NOMASS'),
         ('GL', 'WINDOWS_MATERIAL_GLAZING'),
         ('GA', 'WINDOWS_MATERIAL_GAS'),
    )
    materials_type = models.CharField (max_length=2, choices=MATERIALS_TYPES)


    def __unicode__(self):
        return str(self)


    def __str__(self):
        return force_bytes (self)

