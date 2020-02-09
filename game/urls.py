from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('skys_of_denmark', views.skys_of_denmark, name='skys')
]