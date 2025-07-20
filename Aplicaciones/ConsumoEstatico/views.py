from django.shortcuts import render, redirect
from .models import ConsumoEstatico
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from django.contrib import messages

def editar_consumo_estatico(request, id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    consumos = ConsumoEstatico.objects.filter(id=id)
    if not consumos.exists():
        messages.error(request, 'Consumo estático no encontrado.')
        return redirect('lista_consumo_estatico')
    consumo = consumos.first()
    if request.method == 'POST':
        try:
            consumo.consumoEstatico = float(request.POST.get('consumoEstatico'))
            consumo.save()
            messages.success(request, 'Lectura estática actualizado correctamente.')
            return redirect('lista_consumo_estatico')
        except Exception as e:
            messages.error(request, 'Error al actualizar: ' + str(e))
    consumo.consumoEstatico = str(consumo.consumoEstatico).replace(',', '.')
    return render(request, 'admin/editar_consumo_estatico.html', {'consumo': consumo})

def eliminar_consumo_estatico(request, id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    consumos = ConsumoEstatico.objects.filter(id=id)
    if not consumos.exists():
        messages.error(request, 'Consumo estático no encontrado.')
        return redirect('lista_consumo_estatico')
    consumo = consumos.first()
    consumo.delete()
    messages.success(request, 'Consumo estático eliminado correctamente.')
    return redirect('lista_consumo_estatico')


def agregar_consumo_estatico(request):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    # Usuarios que ya tienen un consumo estático
    usados_ids = ConsumoEstatico.objects.values_list('usuarioSensor_id', flat=True)
    disponibles = UsuarioSensor.objects.exclude(id__in=usados_ids)

    if request.method == 'POST':
        try:
            consumo = float(request.POST.get('consumoEstatico'))
            usuario_sensor_id = request.POST.get('usuarioSensor')

            if not usuario_sensor_id:
                messages.error(request, 'Debe seleccionar un usuario.')
                raise ValueError()

            usuario_sensor = UsuarioSensor.objects.get(id=usuario_sensor_id)

            ConsumoEstatico.objects.create(
                consumoEstatico=consumo,
                usuarioSensor=usuario_sensor
            )

            messages.success(request, 'Consumo estático agregado correctamente.')
            return redirect('lista_consumo_estatico')

        except UsuarioSensor.DoesNotExist:
            messages.error(request, 'El usuario seleccionado no existe.')
        except ValueError:
            messages.error(request, 'Debe ingresar un valor numérico válido.')
        except Exception as e:
            messages.error(request, f'Error al guardar: {str(e)}')

    return render(request, 'admin/agregar_consumo_estatico.html', {
        'usuariosSensoresDisponibles': disponibles
    })

