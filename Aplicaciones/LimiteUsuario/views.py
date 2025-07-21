from django.shortcuts import render, get_object_or_404, redirect
from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.Sensor.models import Sensor
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from Aplicaciones.LimiteUsuario.models import LimiteUsuario
from Aplicaciones.ConsumoEstatico.models import ConsumoEstatico
from Aplicaciones.consumoDinamico.models import ConsumoDinamico
from Aplicaciones.Notificaciones.models import Notificacion
from django.contrib import messages
from django.db.models import ProtectedError
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.utils import timezone


def presentar_limite_usuario(request, id):
    if not request.session.get('es_usuario'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    usuario_id = request.session['usuario_id']
    usuario = get_object_or_404(Usuario, pk=id)
    sensores_asignados = UsuarioSensor.objects.filter(usuario=usuario)

    sensores_con_config = []

    for sensor in sensores_asignados:
        try:
            consumo_estatico = ConsumoEstatico.objects.filter(usuarioSensor=sensor).latest('fechaCorte')
            medicion_base = consumo_estatico.consumoEstatico
        except ConsumoEstatico.DoesNotExist:
            medicion_base = ''

        try:
            limite = LimiteUsuario.objects.filter(usuarioSensor=sensor).latest('fechaCambio')
        except LimiteUsuario.DoesNotExist:
            limite = None

        # Conversión segura
        latitud_str = str(sensor.sensor.latitud).replace(',', '.')
        longitud_str = str(sensor.sensor.longitud).replace(',', '.')
        sensor_id_str = str(sensor.sensor.sensorID)

        sensores_con_config.append({
            'id': sensor.id,
            'sensor': sensor.sensor,
            'sensorID_clean': sensor_id_str,
            'latitud_clean': latitud_str,
            'longitud_clean': longitud_str,
            'ubicacionSensor': sensor.ubicacionSensor,
            'medicionBase': medicion_base,
            'limiteDiario': limite.limiteDiario if limite else '',
            'umbralAlerta': limite.umbralAlerta if limite else '',
            'tiempoMinutos': limite.tiempoMinutos if limite else '',
        })



    return render(request, 'LimiteUsuario/configuraciones.html', {
        'sensores': sensores_con_config,
        'usuario_id': usuario.id
    })



def crearNuevoUsuarioSesor(request, id):
    usuario = get_object_or_404(Usuario, pk=id)

    if request.method == 'POST':
        sensor_id = request.POST.get('sensor_id')
        ubicacion = request.POST.get('ubicacion')
        medicion_base = request.POST.get('medicionBase').replace(',','.')
        limite_diario = request.POST.get('limiteDiario').replace(',','.')
        umbral_alerta = request.POST.get('umbralAlerta').replace(',','.')
        tiempo_minutos = request.POST.get('tiempo').replace(',','.')

        try:
            sensor = Sensor.objects.get(sensorID=sensor_id)
        except Sensor.DoesNotExist:
            print(f"❌ Sensor con ID único '{sensor_id}' no encontrado.")

            messages.error(request, "El sensor ingresado no está registrado.")

            sensores_asignados = UsuarioSensor.objects.filter(usuario=usuario)
            limites = LimiteUsuario.objects.filter(usuarioSensor__usuario=usuario)

            return render(request, 'LimiteUsuario/configuraciones.html', {
                'usuario': usuario,
                'id': usuario.id,
                'sensores': sensores_asignados,
                'limites': limites
            })

        usuario_sensor = UsuarioSensor.objects.create(
            usuario=usuario,
            sensor=sensor,
            ubicacionSensor=ubicacion
        )

        ConsumoEstatico.objects.create(
            usuarioSensor=usuario_sensor,
            consumoEstatico=medicion_base,
            fechaCorte=timezone.now()
        )

        LimiteUsuario.objects.create(
            usuarioSensor=usuario_sensor,
            limiteDiario=limite_diario,
            umbralAlerta=umbral_alerta,
            tiempoMinutos=tiempo_minutos
        )

        messages.success(request, 'Sensor asignado correctamente.')
        return redirect('presentar_limite_usuario', id=usuario.id)

    return redirect('presentar_limite_usuario', id=usuario.id)



def editar_usuario_sensor(request, id):
    usuario_sensor = get_object_or_404(UsuarioSensor, pk=id)
    
    if request.method == 'POST':
        # Leer los datos del formulario
        ubicacion = request.POST.get('ubicacion')
        medicion_base = request.POST.get('medicionBase').replace(',','.')
        limite_diario = request.POST.get('limiteDiario').replace(',','.')
        umbral_alerta = request.POST.get('umbralAlerta').replace(',','.')
        tiempo_minutos = request.POST.get('tiempo').replace(',','.')

        # Actualizar la ubicación en UsuarioSensor
        usuario_sensor.ubicacionSensor = ubicacion
        usuario_sensor.save()

        # Crear un nuevo registro en ConsumoEstatico si hay medición base
        if medicion_base:
            ConsumoEstatico.objects.create(
                usuarioSensor=usuario_sensor,
                consumoEstatico=medicion_base
            )

        # Obtener el último límite registrado para este usuarioSensor
        limite = LimiteUsuario.objects.filter(usuarioSensor=usuario_sensor).order_by('-fechaCambio').first()
        if limite:
            # Actualizar el último registro
            limite.limiteDiario = limite_diario
            limite.umbralAlerta = umbral_alerta
            limite.tiempoMinutos = tiempo_minutos
            limite.save()
        else:
            # Crear nuevo si no existe ninguno
            LimiteUsuario.objects.create(
                usuarioSensor=usuario_sensor,
                limiteDiario=limite_diario,
                umbralAlerta=umbral_alerta,
                tiempoMinutos=tiempo_minutos
            )

        messages.success(request, 'Configuración actualizada correctamente.')
        return redirect('presentar_limite_usuario', id=usuario_sensor.usuario.id)

    # Si es GET, puedes mostrar un template opcional (aunque usas modal JS)
    return render(request, 'LimiteUsuario/editar_sensor.html', {
        'sensor': usuario_sensor,
    })




def eliminar_usuario_sensor(request, id):
    usuario_sensor = get_object_or_404(UsuarioSensor, pk=id)
    usuario_id = usuario_sensor.usuario.id

    ConsumoEstatico.objects.filter(usuarioSensor=usuario_sensor).delete()
    LimiteUsuario.objects.filter(usuarioSensor=usuario_sensor).delete()
    ConsumoDinamico.objects.filter(usuarioSensor=usuario_sensor).delete()

    usuario_sensor.delete()

    messages.success(request, "Sensor y datos asociadas eliminadas correctamente.")
    return redirect('presentar_limite_usuario', id=usuario_id)






#PARA CLOUD






def nuevoAsignacion(request):

    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    usuarios = Usuario.objects.all().order_by('nombreUsuario')
    sensores_asignados = UsuarioSensor.objects.values_list('sensor_id', flat=True)
    sensores = Sensor.objects.exclude(sensorID__in=sensores_asignados).order_by('nombreSensor')

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        sensor_id = request.POST.get('sensor_id')
        medicion_base = request.POST.get('medicionBase', '0').replace(',', '.')
        limite_diario = request.POST.get('limiteDiario', '0').replace(',', '.')
        umbral_alerta = request.POST.get('umbralAlerta', '0').replace(',', '.')
        tiempo_minutos = 1

        usuario = get_object_or_404(Usuario, pk=usuario_id)

        try:
            sensor = Sensor.objects.get(sensorID=sensor_id)
        except Sensor.DoesNotExist:
            messages.error(request, f"❌ Medidor con Número #{sensor_id} no está registrado.")
            return render(request, 'asingacion/crear_asignacion.html', {
                'usuarios': usuarios,
                'sensores': sensores,
                'usuario_id': usuario_id,
                'sensor_id': sensor_id,
                'medicion_base': medicion_base,
                'limite_diario': limite_diario,
                'umbral_alerta': umbral_alerta,
                'tiempo_minutos': tiempo_minutos
            })

        usuario_sensor = UsuarioSensor.objects.create(
            usuario=usuario,
            sensor=sensor,
            ubicacionSensor= "Casa 1"
        )

        ConsumoEstatico.objects.create(
            usuarioSensor=usuario_sensor,
            consumoEstatico=medicion_base,
            fechaCorte=timezone.now()
        )

        LimiteUsuario.objects.create(
            usuarioSensor=usuario_sensor,
            limiteDiario=limite_diario,
            umbralAlerta=umbral_alerta,
            tiempoMinutos=tiempo_minutos
        )

        messages.success(request, f"✅ Medidor Número #{sensor_id} asignado correctamente a {usuario.nombreUsuario}.")
        return redirect('listaAsignacion')  

    return render(request, 'asingacion/crear_asignacion.html', {
        'usuarios': usuarios,
        'sensores': sensores
    })


def editar_asignacion(request, asignacion_id):

    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    
    asignacion = get_object_or_404(UsuarioSensor, id=asignacion_id)

    consumo_obj = ConsumoEstatico.objects.filter(usuarioSensor=asignacion).order_by('fechaCorte').first()
    limite_obj = LimiteUsuario.objects.filter(usuarioSensor=asignacion).order_by('-fechaCambio').first()

    if request.method == 'POST':
        medicion_base = request.POST.get('medicionBase', '0').replace(',', '.')
        limite_diario = request.POST.get('limiteDiario', '0').replace(',', '.')
        umbral_alerta = request.POST.get('umbralAlerta', '0').replace(',', '.')
        tiempo_minutos = request.POST.get('tiempoMinutos', '0').replace(',', '.')

        asignacion.ubicacionSensor = "Casa 1"
        asignacion.save()

        if consumo_obj:
            consumo_obj.consumoEstatico = medicion_base
            consumo_obj.save()
        else:
            ConsumoEstatico.objects.create(
                usuarioSensor=asignacion,
                consumoEstatico=medicion_base
            )

        if limite_obj:
            limite_obj.limiteDiario = limite_diario
            limite_obj.umbralAlerta = umbral_alerta
            limite_obj.tiempoMinutos = tiempo_minutos
            limite_obj.save()
        else:
            LimiteUsuario.objects.create(
                usuarioSensor=asignacion,
                limiteDiario=limite_diario,
                umbralAlerta=umbral_alerta,
                tiempoMinutos=tiempo_minutos
            )

        messages.success(request, "Asignación actualizada correctamente.")
        return redirect('listaAsignacion') 

    # Convertir valores con punto como separador
    medicion_base = '{:.2f}'.format(consumo_obj.consumoEstatico) if consumo_obj else ''
    limite_diario = '{:.2f}'.format(limite_obj.limiteDiario) if limite_obj else ''
    umbral_alerta = '{:.2f}'.format(limite_obj.umbralAlerta) if limite_obj else ''
    tiempo_minutos = str(limite_obj.tiempoMinutos) if limite_obj else ''

    context = {
        'asignacion': asignacion,
        'medicion_base': medicion_base,
        'limite_diario': limite_diario,
        'umbral_alerta': umbral_alerta,
        'tiempo_minutos': tiempo_minutos
    }

    return render(request, 'asingacion/editar_asignacion.html', context)



def eliminar_asignacion(request, asignacion_id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    if request.method == 'POST':
        asignacion = get_object_or_404(UsuarioSensor, id=asignacion_id)

        try:
            ConsumoEstatico.objects.filter(usuarioSensor=asignacion).delete()
            ConsumoDinamico.objects.filter(usuarioSensor=asignacion).delete()
            LimiteUsuario.objects.filter(usuarioSensor=asignacion).delete()
            Notificacion.objects.filter(usuarioSensor=asignacion).delete()

            asignacion.delete()
            messages.success(request, "✅ Asignación y todos sus registros asociados fueron eliminados.")
        except ProtectedError as e:
            messages.error(request, f"❌ No se pudo eliminar por restricciones: {e}")

        return redirect('listaAsignacion')



from django.core.serializers.json import DjangoJSONEncoder
import json

def listaAsignacion(request):

    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    
    asignaciones = UsuarioSensor.objects.select_related('sensor', 'usuario').all()

    asignaciones_js = []
    for a in asignaciones:
        asignaciones_js.append({
            'id': a.id,
            'sensorID': a.sensor.sensorID,
            'latitud': a.sensor.latitud,
            'longitud': a.sensor.longitud,
            'ubicacion': a.ubicacionSensor,
            'usuario': a.usuario.nombreUsuario
        })

    context = {
        'asignaciones': asignaciones,
        'asignaciones_js': json.dumps(asignaciones_js, cls=DjangoJSONEncoder)
    }

    return render(request, 'asingacion/index.html', context)




@csrf_exempt
def enviar_pdf_telegram(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if not all(key in data for key in ['pdf_url', 'chat_id', 'mensaje']):
                return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)
            
            token = "7992982183:AAH2kYLicJ5zM6NrAYExc_IowviLRJ723zo"
            
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data={
                    'chat_id': data['chat_id'],
                    'text': data['mensaje'],
                    'parse_mode': 'Markdown'
                }
            )
            
            if data['pdf_url']:
                from django.conf import settings
                pdf_full_url = request.build_absolute_uri(data['pdf_url'])
                print("URL completa del PDF:", pdf_full_url)
                
                pdf_response = requests.get(pdf_full_url, stream=True)
                pdf_response.raise_for_status()
                
                files = {'document': ('reporte.pdf', pdf_response.content)}
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendDocument",
                    data={'chat_id': data['chat_id']},
                    files=files
                )
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)