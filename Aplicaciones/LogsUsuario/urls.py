from django.urls import path
from .views import eliminar_log_usuario, agregar_log_usuario
from . import views


urlpatterns = [
    
    path('agregar_log_usuario/', agregar_log_usuario, name='agregar_log_usuario'),
    path('editar_log_usuario/<int:id>/', views.editar_log_usuario, name='editar_log_usuario'),
    path('eliminar_log_usuario/<int:id>/', eliminar_log_usuario, name='eliminar_log_usuario'),
]