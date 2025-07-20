from django.shortcuts import render, redirect
from .models import LogUsuario
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from Aplicaciones.Usuario.models import Usuario



def agregar_log_usuario(request):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            fecha_cambio = parse_datetime(request.POST.get('fechaCambio'))
            evento = request.POST.get('evento')
            descripcion = request.POST.get('descripcion')
            usuario_id = request.POST.get('usuario')
            
            # Validaciones
            if not fecha_cambio:
                messages.error(request, 'Formato de fecha inválido')
                return redirect('agregar_log_usuario')
                
            usuario = Usuario.objects.get(id=usuario_id)
            
            # Crear el registro
            LogUsuario.objects.create(
                fechaCambio=fecha_cambio,
                evento=evento,
                descripcion=descripcion,
                usuario=usuario
            )
            
            messages.success(request, 'Registro de historial creado exitosamente!')
            return redirect('ver_logs_usuario')
            
        except Exception as e:
            messages.error(request, f'Error al crear registro: {str(e)}')
    
    usuarios = Usuario.objects.all()
    return render(request, 'admin/agregar_log_usuario.html', {
        'usuarios': usuarios
    })

def eliminar_log_usuario(request, id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    logs = LogUsuario.objects.filter(id=id)
    if not logs.exists():
        messages.error(request, 'Log de usuario no encontrado.')
        return redirect('ver_logs_usuario')
    log = logs.first()
    log.delete()
    messages.success(request, 'Log de usuario eliminado correctamente.')
    return redirect('ver_logs_usuario')

def editar_log_usuario(request, id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    log = get_object_or_404(LogUsuario, id=id)

    if request.method == 'POST':
        # Obtenemos los datos enviados
        fecha_cambio_str = request.POST.get('fechaCambio')
        evento = request.POST.get('evento')
        descripcion = request.POST.get('descripcion')

        # Parsear la fecha de tipo string a datetime
        fecha_cambio = parse_datetime(fecha_cambio_str)

        if fecha_cambio is None:
            messages.error(request, 'Formato de fecha/hora inválido.')
        else:
            # Actualizamos el registro
            log.fechaCambio = fecha_cambio
            log.evento = evento
            log.descripcion = descripcion
            log.save()
            messages.success(request, 'Log actualizado correctamente.')
            return redirect('ver_logs_usuario')  # O la url que corresponda

    return render(request, 'admin/editar_log_usuario.html', {'log': log})