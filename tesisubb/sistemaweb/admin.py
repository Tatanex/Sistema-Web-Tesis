# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Comparar
from .models import Material
from .models import Simular
from .models import Combinar
from .models import Modificar

admin.site.register(Comparar)
admin.site.register(Material)
admin.site.register(Simular)
admin.site.register(Combinar)
admin.site.register(Modificar)