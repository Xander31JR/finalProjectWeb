from django.urls import path
from . import views


urlpatterns = [

    path('agregar_tipo_mensaje/', views.agregar_tipo_mensaje, name='agregar_tipo_mensaje'),
    path('editar_tipo_mensaje/<int:id>/', views.editar_tipo_mensaje, name='editar_tipo_mensaje'),
    path('eliminar_tipo_mensaje/<int:id>/', views.eliminar_tipo_mensaje, name='eliminar_tipo_mensaje'),

]
