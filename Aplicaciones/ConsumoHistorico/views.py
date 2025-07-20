from django.shortcuts import render, redirect
from .models import ConsumoHistorico
from django.contrib import messages
from Aplicaciones.UsuarioSensor.models import UsuarioSensor


def agregar_consumo_historico(request):

    usuarios_sensores = UsuarioSensor.objects.all()

    if request.method == 'POST':
        try:
            consumo_total = float(request.POST.get('consumoTotal'))
            max_consumo = float(request.POST.get('maxConsumo'))
            min_consumo = float(request.POST.get('minConsumo'))
            fecha_periodo = request.POST.get('fechaPeriodo')
            usuario_sensor_id = request.POST.get('usuarioSensor')

            usuario_sensor = UsuarioSensor.objects.get(id=usuario_sensor_id)

            ConsumoHistorico.objects.create(
                consumoTotal=consumo_total,
                maxConsumo=max_consumo,
                minConsumo=min_consumo,
                fechaPeriodo=fecha_periodo,
                usuarioSensor=usuario_sensor
            )

            messages.success(request, 'Consumo histórico agregado correctamente.')
            return redirect('lista_consumo_historico')

        except ValueError:
            messages.error(request, 'Los valores deben ser válidos.')
        except UsuarioSensor.DoesNotExist:
            messages.error(request, 'Usuario-Sensor no válido.')
        except Exception as e:
            messages.error(request, f'Error al agregar: {str(e)}')

    return render(request, 'admin/agregar_consumo_historico.html', {
        'usuarios_sensores': usuarios_sensores
    })

def editar_consumo_historico(request, id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    historicos = ConsumoHistorico.objects.filter(id=id)
    if not historicos.exists():
        messages.error(request, 'Consumo histórico no encontrado.')
        return redirect('lista_consumo_historico')
    historico = historicos.first()
    if request.method == 'POST':
        try:
            historico.consumoTotal = float(request.POST.get('consumoTotal'))
            historico.maxConsumo = float(request.POST.get('maxConsumo'))
            historico.minConsumo = float(request.POST.get('minConsumo'))
            historico.fechaPeriodo = request.POST.get('fechaPeriodo')
            historico.save()
            messages.success(request, 'Consumo histórico actualizado correctamente.')
            return redirect('lista_consumo_historico')
        except Exception as e:
            messages.error(request, 'Error al actualizar: ' + str(e))

    consumoTotal_str = str(historico.consumoTotal).replace(',', '.')
    maxConsumo_str = str(historico.maxConsumo).replace(',', '.')
    minConsumo_str = str(historico.minConsumo).replace(',', '.')

    return render(request, 'admin/editar_consumo_historico.html', {
        'historico': historico,
        'consumoTotal_str': consumoTotal_str,
        'maxConsumo_str': maxConsumo_str,
        'minConsumo_str': minConsumo_str
    })


def eliminar_consumo_historico(request, id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    historicos = ConsumoHistorico.objects.filter(id=id)
    if not historicos.exists():
        messages.error(request, 'Consumo histórico no encontrado.')
        return redirect('lista_consumo_historico')
    historico = historicos.first()
    historico.delete()
    messages.success(request, 'Consumo histórico eliminado correctamente.')
    return redirect('lista_consumo_historico')