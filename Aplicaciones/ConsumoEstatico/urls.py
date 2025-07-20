from django.urls import path
from . import views
urlpatterns = [


    path('agregar_consumo_estatico', views.agregar_consumo_estatico, name='agregar_consumo_estatico'),
    path('editar_consumo_estatico/<int:id>/', views.editar_consumo_estatico, name='editar_consumo_estatico'),
    path('eliminar_consumo_estatico/<int:id>/', views.eliminar_consumo_estatico, name='eliminar_consumo_estatico'),
]