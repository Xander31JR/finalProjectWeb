from django.urls import path
from . import views


urlpatterns = [
    path('lista_consumo_historico/', views.lista_consumo_historico, name='lista_consumo_historico'),
    path('log_usuario/', views.ver_logs_usuario, name='ver_logs_usuario'),
    path('tipo_mensajes/', views.lista_tipo_mensaje, name='lista_tipo_mensaje'),
    path('notificaciones/', views.lista_notificaciones, name='lista_notificaciones'),
    path('consumo_estatico/', views.lista_consumo_estatico, name='lista_consumo_estatico'),
    path('consumo_dinamico/', views.lista_consumo_dinamico, name='lista_consumo_dinamico'),
    path('', views.IniciarSesion, name="IniciarSesion" ),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),

]
