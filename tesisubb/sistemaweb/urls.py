from django.conf.urls import url
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from . import views



urlpatterns = [
    # url('/', views.index, name='index'),
    url('index', views.indexView, name='index'),

    url ('upload', views.upload_file_view, name='upload_image_view'),
    url ('(?P<pk>[0-9]+)/$', views.simularView),

]


