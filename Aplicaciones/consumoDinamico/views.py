from django.shortcuts import render, redirect
from .models import ConsumoDinamico
from django.contrib import messages
from Aplicaciones.UsuarioSensor.models import UsuarioSensor  


def agregar_consumo_dinamico(request):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    if request.method == 'POST':
        try:
            consumo = float(request.POST.get('consumoDinamico'))
            usuario_sensor_id = request.POST.get('usuarioSensor')
            
            if not usuario_sensor_id:
                messages.error(request, 'Debe seleccionar un usuario y medidor.')
                return redirect('agregar_consumo_dinamico')
                
            usuario_sensor = UsuarioSensor.objects.get(id=usuario_sensor_id)
            
            ConsumoDinamico.objects.create(
                consumoDinamico=consumo,
                usuarioSensor=usuario_sensor
            )
            
            messages.success(request, 'Consumo dinámico agregado correctamente.')
            return redirect('lista_consumo_dinamico')
            
        except ValueError:
            messages.error(request, 'El consumo debe ser un número válido.')
        except UsuarioSensor.DoesNotExist:
            messages.error(request, 'Usuario y medidor no encontrado.')
        except Exception as e:
            messages.error(request, f'Error al agregar: {str(e)}')
    
    usuarios_sensores = UsuarioSensor.objects.all()
    return render(request, 'admin/agregar_consumo_dinamico.html', {
        'usuarios_sensores': usuarios_sensores
    })

def editar_consumo_dinamico(request, id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    consumos = ConsumoDinamico.objects.filter(id=id)
    if not consumos.exists():
        messages.error(request, 'Consumo dinámico no encontrado.')
        return redirect('lista_consumo_dinamico')
    consumo = consumos.first()
    if request.method == 'POST':
        try:
            consumo.consumoDinamico = float(request.POST.get('consumoDinamico'))
            consumo.save()
            messages.success(request, 'Consumo dinámico actualizado correctamente.')
            return redirect('lista_consumo_dinamico')
        except Exception as e:
            messages.error(request, 'Error al actualizar: ' + str(e))
    consumo_str = str(consumo.consumoDinamico).replace(',', '.')
    return render(request, 'admin/editar_consumo_dinamico.html', {'consumo': consumo_str })

def eliminar_consumo_dinamico(request, id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    consumos = ConsumoDinamico.objects.filter(id=id)
    if not consumos.exists():
        messages.error(request, 'Consumo dinámico no encontrado.')
        return redirect('lista_consumo_dinamico')
    consumo = consumos.first()
    consumo.delete()
    messages.success(request, 'Consumo dinámico eliminado correctamente.')
    return redirect('lista_consumo_dinamico')