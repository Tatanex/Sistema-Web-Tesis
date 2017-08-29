# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Construccion
from .models import Material
from .models import Simular
from .models import ReporteSimulacion

admin.site.register(Construccion)
admin.site.register(Material)
admin.site.register(Simular)
admin.site.register(ReporteSimulacion)