from django.urls import path
from . import  views

urlpatterns = [
    path('<id>', views.presentar_limite_usuario, name="presentar_limite_usuario"),
    path('nuevoUsuarioSensor/<id>', views.crearNuevoUsuarioSesor, name='crearNuevoUsuarioSesor'),
    path('editarUsuarioSensor/<int:id>', views.editar_usuario_sensor, name='editarUsuarioSensor'),
    path('eliminarUsuarioSensor/<int:id>/', views.eliminar_usuario_sensor, name='eliminar_usuario_sensor'),

    path('listaAsignacion/', views.listaAsignacion, name='listaAsignacion'),
    path('nuevoAsignacion/', views.nuevoAsignacion, name='nuevoAsignacion'),

    path('editar_asignacion/<int:asignacion_id>', views.editar_asignacion, name='editar_asignacion'),
    path('eliminar_asignacion/<int:asignacion_id>', views.eliminar_asignacion, name='eliminar_asignacion'),


    path('enviarPDF/', views.enviar_pdf_telegram), 


]