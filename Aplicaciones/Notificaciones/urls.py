from django.urls import path
from . import views 

urlpatterns = [


    path('agregar/', views.agregar_notificacion, name='agregar_notificacion'),

    path('notificaciones/<int:sensor_id>/', views.obtener_notificaciones_sensor, name='obtener_notificaciones_sensor'),
    
    path('notificacionesTexto/<int:sensor_id>/', views.obtener_notificaciones_sensor_texto, name='obtener_notificaciones_sensor_texto'),


    path('notificaciones/sensor/<int:id>/', views.ver_notificaciones_por_usuario, name="ver_notificaciones_por_usuario"),





    path('estadistica/<id>', views.estadisticaPresenracion, name="estadisticaPresenracion"),

    path('estadisticas-geograficas', views.estadisticas_geograficas, name="estadisticas_geograficas"),
    


    path("reporte/consumo/<int:sensor_id>/", views.reporte_consumo_json, name="reporte_consumo_json"),

    path("reporte/consumo/pie/<int:sensor_id>/", views.reporte_consumo_pie, name="reporte_consumo_pie"),

    path('eliminar_notificacion/<int:id>/', views.eliminar_notificacion, name='eliminar_notificacion'),




    path('admin-estadisticas-geograficas', views.admin_estadisticas_geograficas, name="admin-estadisticas_geograficas"),
    
    path('admin-estadisticas-geograficas-avanzadas', views.admin_estadisticas_geograficas_avanzadas, name="admin_estadisticas_geograficas_avanzadas"),

    path('consumo-dinamico-hoy', views.consumo_dinamico_hoy, name="consumo-dinamico-hoy"),


    path('editar_notificacion/<int:id>/', views.editar_notificacion, name='editar_notificacion'),





]