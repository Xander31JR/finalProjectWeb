from django.urls import path
from . import views

urlpatterns = [
    path('lista_sensor/', views.lista_sensor, name='lista_sensor'),
    path('agregar_sensor/', views.agregar_sensor, name='agregar_sensor'),
    path('editar_sensor/<int:sensorID>/', views.editar_sensor, name='editar_sensor'),
    path('eliminar_sensor/<int:sensorID>/', views.eliminar_sensor, name='eliminar_sensor'),



]