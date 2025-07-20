from django.urls import path
from . import views

urlpatterns = [

    ################ ESTA RUTA ES PARA EL MENU CENTRAL##############
    path('sesionIniciada/', views.menuCentral, name='menuCentral'), 

    path('perfil/', views.perfil_usuario, name='perfil_usuario'),

    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('verify_email/', views.verify_email, name='verify_email'), 


    path('lista_usuario/', views.lista_usuario, name='lista_usuario'), 
    path('agregar_usuario/', views.agregar_usuario, name='agregar_usuario'), 
    path('editar_usuario/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),


    path('establecer_password/', views.establecer_password, name='establecer_password'), 



]