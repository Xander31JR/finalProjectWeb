from django.urls import path
from .views import editar_consumo_historico, eliminar_consumo_historico, agregar_consumo_historico

urlpatterns = [
    path('agregar_consumo_historico/',agregar_consumo_historico, name='agregar_consumo_historico'),
    path('editar_consumo_historico/<int:id>/', editar_consumo_historico, name='editar_consumo_historico'),
    path('eliminar_consumo_historico/<int:id>/', eliminar_consumo_historico, name='eliminar_consumo_historico'),
]