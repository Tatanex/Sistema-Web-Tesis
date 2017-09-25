from django.conf.urls import url
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from . import views



urlpatterns = [
    # url('/', views.index, name='index'),
    url('index', views.indexView, name='index'),
    url('upload', views.cargar_archivo_simulacion_view, name='upload'),
    url('ver_simulaciones', views.ver_simulaciones, name='ver_simulaciones'),
    url(r'^simular/(\d+)/$', views.simularView, name='simular'),
    url(r'^simular/(\d+)/submit$', views.submit, name='submit'),
    url(r'^ver/simulacion_(\d+)/$', views.ver, name='ver'),

    url('comparar', views.compararidf, name='comparar'),
    url('diferencia_comparacion/(\d+)/$', views.diferencia_comparacion, name='diferencia_comparacion'),

    # url ('detalle/objeto_objeto_(\d+)/$', views.ver_objeto, name='ver_objeto')
    url ('detalle/(\d+)/(\w+)/(\w+)/$', views.ver_objeto, name='ver_objeto'),
    url ('detalle/(\d+)/(\w+:\w+)/(\w+)/$', views.ver_objeto, name='ver_objeto'),
    url ('ver_comparaciones', views.ver_comparaciones, name='ver_comparaciones'),
    url ('ver_comparacion_(\d+)/$', views.ver_comparaciones, name='ver_comparaciones'),

    url ('modificar', views.modificar, name='modificar'),





]


