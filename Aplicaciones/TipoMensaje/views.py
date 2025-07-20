from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import TipoMensaje
from django.db.models import ProtectedError


#agragar tipomensjae
def agregar_tipo_mensaje(request):
    if request.method == 'POST':
        try:
            tipo_alerta = request.POST.get('tipoAlerta')
            mensaje_default = request.POST.get('mensaje_default')
            
            TipoMensaje.objects.create(
                tipoAlerta=tipo_alerta,
                mensaje_default=mensaje_default
            )
            
            messages.success(request, 'Tipo de mensaje creado exitosamente!')
            return redirect('lista_tipo_mensaje')
            
        except Exception as e:
            messages.error(request, f'Error al crear tipo de mensaje: {str(e)}')
    
    return render(request, 'admin/agregar_tipo_mensaje.html')

# Editar TipoMensaje
def editar_tipo_mensaje(request, id):
    tipo_mensaje = get_object_or_404(TipoMensaje, id=id)
    if request.method == 'POST':
        try:
            tipo_mensaje.tipoAlerta = request.POST.get('tipoAlerta')
            tipo_mensaje.mensaje_default = request.POST.get('mensaje_default')
            tipo_mensaje.save()
            messages.success(request, 'Tipo de mensaje actualizado correctamente.')
            return redirect('lista_tipo_mensaje')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')
    return render(request, 'admin/editar_tipo_mensaje.html', {'tipo': tipo_mensaje})


# Eliminar TipoMensaje
def eliminar_tipo_mensaje(request, id):
    try:
        tipo_mensaje = TipoMensaje.objects.filter(id=id).first()
        
        if not tipo_mensaje:
            messages.error(request, 'El tipo de mensaje no existe.')
            return redirect('lista_tipo_mensaje')
        
        tipo_mensaje.delete()
        messages.success(request, 'Tipo de mensaje eliminado correctamente.')
        
    except ProtectedError:
        messages.error(
            request,
            'No se puede eliminar este tipo de mensaje porque está siendo utilizado. '
            'Elimine primero las notificaciones que lo usan o cambie su tipo.'
        )
        
    except Exception as e:
        messages.error(request, f'Error al eliminar: {str(e)}')
    
    return redirect('lista_tipo_mensaje')
