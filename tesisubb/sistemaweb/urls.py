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
    url('detalle_comparacion/(\d+)/$', views.detalle_comparacion, name='detalle_comparacion'),
    url('detalle/(\d+)/(\w+)/(\w+)/$', views.ver_objeto, name='ver_objeto'),
    url('detalle/(\d+)/(\w+:\w+)/(\w+)/$', views.ver_objeto, name='ver_objeto'),
    url('ver_comparaciones', views.ver_comparaciones, name='ver_comparaciones'),
    url('ver_comparacion_(\d+)/$', views.ver_comparaciones, name='ver_comparaciones'),

    url('cargar_modificacion', views.cargar_modificacion, name='cargar_modificacion'),
    url('modificar/(\d+)/(\w+)/(\w+)/$', views.modificar_objeto, name='modificar_objeto'),
    # url('/(\d+)$', views.modificar_submit, name='modificar_submit'),
    url('ver_modificaciones', views.ver_modificaciones, name='ver_modificaciones'),
    url('modificar/(\d+)$', views.detalle_modificacion, name='detalle_modificacion'),



    url('crear_materials$', views.crear_materials, name='crear_materials'),
    url('ver_materials$', views.ver_materials, name='ver_materials'),







]
