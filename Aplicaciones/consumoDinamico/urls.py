from django.urls import path
from .views import editar_consumo_dinamico, eliminar_consumo_dinamico, agregar_consumo_dinamico

urlpatterns = [

    path('agregar_consumo_dinamico/', agregar_consumo_dinamico, name='agregar_consumo_dinamico'),
    path('editar_consumo_dinamico/<int:id>/', editar_consumo_dinamico, name='editar_consumo_dinamico'),
    path('eliminar_consumo_dinamico/<int:id>/', eliminar_consumo_dinamico, name='eliminar_consumo_dinamico'),
]