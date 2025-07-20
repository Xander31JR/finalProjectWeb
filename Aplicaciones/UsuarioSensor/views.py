# views.py en la aplicación UsuarioSensor
from django.shortcuts import render, redirect, get_object_or_404
from .models import UsuarioSensor
from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.Sensor.models import Sensor
from django.contrib import messages
from django.contrib.auth.hashers import make_password


def panel_admin(request):
    if not request.session.get('es_admin'):
        return redirect('login') 

    usuarios = Usuario.objects.all()  
    sensores = Sensor.objects.all() 
    asignaciones = UsuarioSensor.objects.all()  

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        sensor_id = request.POST.get('sensor')
        ubicacion = request.POST.get('ubicacion')

        # Crear una nueva asignación
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            sensor = Sensor.objects.get(id=sensor_id)
            asignacion = UsuarioSensor(usuario=usuario, sensor=sensor, ubicacionSensor=ubicacion)
            asignacion.save()
            messages.success(request, 'Sensor asignado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al asignar sensor: {str(e)}')

    return render(request, 'admin/paneladmin.html', {
        'usuarios': usuarios,
        'sensores': sensores,
        'asignaciones': asignaciones,
    })







