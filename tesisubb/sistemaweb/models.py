# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.


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
    simular_clima = models.FileField(upload_to='epw/')
    simular_archivo_idf = models.FileField(upload_to='idf/')

    def __unicode__(self):  # __unicode__ on Python 2
        return self.simular_clima





class ReporteSimulacion(models.Model):
    reporte_id = models.AutoField(primary_key=True)
    reporte_totalenergy_totalsite = models.FloatField()
    reporte_totalenergy_totalsource = models.FloatField()
    reporte_distric_heating_heating = models.FloatField()
    reporte_distric_time_etpoint = models.FloatField()
    reporte_heating_intensity_hvac = models.FloatField()

    def __unicode__(self):  # __unicode__ on Python 2
        return self.reporte_id



