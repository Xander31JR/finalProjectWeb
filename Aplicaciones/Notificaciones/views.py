from django.shortcuts import render, get_object_or_404, redirect
from Aplicaciones.Usuario.models import Usuario
from django.http import JsonResponse
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from django.contrib import messages
from Aplicaciones.TipoMensaje.models import TipoMensaje
import json
from datetime import datetime, timedelta, timezone
from django.utils.timezone import now, localtime
from django.db.models import Sum
from django.utils.dateparse import parse_date
from Aplicaciones.Sensor.models import Sensor
from Aplicaciones.ConsumoHistorico.models import ConsumoHistorico
from datetime import datetime, time
from Aplicaciones.Notificaciones.models import Notificacion
from Aplicaciones.consumoDinamico.models import ConsumoDinamico
from Aplicaciones.ConsumoEstatico.models import ConsumoEstatico
from Aplicaciones.LimiteUsuario.models import LimiteUsuario




def agregar_notificacion(request):
    
    if request.method == 'POST':
        try:
            mensaje = request.POST.get('mensaje')
            usuario_sensor_id = request.POST.get('usuarioSensor')
            tipo_mensaje_id = request.POST.get('tipoMensaje')
            estado = 'estado' in request.POST
            
            usuario_sensor = UsuarioSensor.objects.get(id=usuario_sensor_id)
            tipo_mensaje = TipoMensaje.objects.get(id=tipo_mensaje_id)
            
            Notificacion.objects.create(
                mensaje=mensaje,
                usuarioSensor=usuario_sensor,
                tipoMensaje=tipo_mensaje,
                estado=estado
            )
            
            messages.success(request, 'Notificación creada exitosamente!')
            return redirect('lista_notificaciones')
            
        except Exception as e:
            messages.error(request, f'Error al crear notificación: {str(e)}')
    
    usuarios_sensores = UsuarioSensor.objects.select_related('usuario', 'sensor').all()
    tipos_mensaje = TipoMensaje.objects.all()
    
    return render(request, 'admin/agregar_notificaciones.html', {
        'usuarios_sensores': usuarios_sensores,
        'tipos_mensaje': tipos_mensaje
    })


def ver_notificaciones_por_usuario(request, id):

    if not request.session.get('es_usuario'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 

    usuario_id = request.session['usuario_id']
    usuario = get_object_or_404(Usuario, pk=id)
    sensores = UsuarioSensor.objects.filter(usuario=usuario)
    
    return render(request, 'Notificaciones/panelNotificaciones.html', {
        'usuario': usuario,
        'sensores': sensores,
        'usuario_id': usuario_id
    })

#@csrf_exempt
#def recibir_datos(request):
#    if request.method == 'POST':
#        try:
#            data = json.loads(request.body)
#            sensor_id = data.get('sensor_id')
#            consumo = data.get('consumoLitro')
#
#            # Busca el usuarioSensor relacionado al sensor_id
#            usuario_sensor = UsuarioSensor.objects.filter(sensor__sensorID=sensor_id).first()
#            if not usuario_sensor:
#                return JsonResponse({'error': 'Sensor no encontrado'}, status=404)
#
#            # Busca el tipo de mensaje (ajusta el filtro según tu lógica)
#            tipo_mensaje = TipoMensaje.objects.filter(tipoAlerta='Consumo').first()
#            if not tipo_mensaje:
#                tipo_mensaje = TipoMensaje.objects.first()  # fallback
#
#            # Crea la notificación
#            mensaje = f"Consumo reportado: {consumo} litros"
#            Notificacion.objects.create(
#                mensaje=mensaje,
#                usuarioSensor=usuario_sensor,
#                tipoMensaje=tipo_mensaje,
#                fechaEnvio=timezone.now()
#            )
#
#            return JsonResponse({'status': 'ok', 'mensaje': mensaje})
#        except Exception as e:
#            return JsonResponse({'error': str(e)}, status=400)
#    return JsonResponse({'error': 'Método no permitido'}, status=405)


def eliminar_notificacion(request, id):

    
    notificaciones = Notificacion.objects.filter(id=id)
    if not notificaciones.exists():
        messages.error(request, 'Notificación no encontrada.')
        return redirect('lista_notificaciones')
    notificacion = notificaciones.first()
    notificacion.delete()
    messages.success(request, 'Notificación eliminada correctamente.')
    return redirect('lista_notificaciones')


def editar_notificacion(request, id):

    notificacion = get_object_or_404(Notificacion, id=id)
    if request.method == 'POST':
        notificacion.mensaje = request.POST.get('mensaje')
        notificacion.estado = 'estado' in request.POST
        notificacion.save()
        messages.success(request, 'Notificación actualizada correctamente.')
        return redirect('lista_notificaciones')
    return render(request, 'admin/editar_notificacion.html', {'notificacion': notificacion})



def obtener_notificaciones_sensor_texto(request, sensor_id):
    notificaciones = Notificacion.objects.filter(usuarioSensor__id=sensor_id).order_by('-fechaEnvio')
    
    data = [
        {
            'mensaje': n.mensaje,
            'fechaEnvio': localtime(n.fechaEnvio).strftime("%Y-%m-%d %H:%M"), 
            'tipo': n.tipoMensaje.tipoAlerta
        }
        for n in notificaciones
    ]
    
    return JsonResponse({'notificaciones': data})






def obtener_notificaciones_sensor(request, sensor_id):
    usuario_sensor = UsuarioSensor.objects.filter(id=sensor_id).first()
    if not usuario_sensor:
        return JsonResponse({'error': 'Sensor no encontrado'}, status=404)

    notificaciones = Notificacion.objects.filter(usuarioSensor__id=sensor_id).order_by('-fechaEnvio')
    mensajes_data = [
        {
            'mensaje': n.mensaje,
            'fechaEnvio': localtime(n.fechaEnvio).strftime("%Y-%m-%d %H:%M"),
            'tipo': n.tipoMensaje.tipoAlerta
        }
        for n in notificaciones
    ]

    ahora_local = localtime()
    inicio_dia = datetime.combine(ahora_local.date(), time.min).replace(tzinfo=ahora_local.tzinfo)    
    fin_dia = datetime.combine(ahora_local.date(), time.max).replace(tzinfo=ahora_local.tzinfo)

    inicio_mes = datetime.combine(ahora_local.replace(day=1).date(), time.min).replace(tzinfo=ahora_local.tzinfo)
    consumo_diario = ConsumoDinamico.objects.filter(
        usuarioSensor=usuario_sensor,
        fechaCorte__gte=inicio_dia,
        fechaCorte__lte=fin_dia
    ).aggregate(total=Sum('consumoDinamico'))['total'] or 0

    consumo_mensual = ConsumoDinamico.objects.filter(
        usuarioSensor=usuario_sensor,
        fechaCorte__gte=inicio_mes,
        fechaCorte__lte=ahora_local
    ).aggregate(total=Sum('consumoDinamico'))['total'] or 0

    consumo_estatico = ConsumoEstatico.objects.filter(usuarioSensor=usuario_sensor).order_by('-fechaCorte').first()
    lectura_base = consumo_estatico.consumoEstatico if consumo_estatico else 0

    limite = LimiteUsuario.objects.filter(usuarioSensor=usuario_sensor).order_by('-fechaCambio').first()
    limite_diario = limite.limiteDiario if limite else 3000
    umbral_mensual = limite.umbralAlerta if limite else 30000


    ultimo_consumo = ConsumoDinamico.objects.filter(usuarioSensor=usuario_sensor).order_by('-fechaCorte').first()
    hora_ultimo = localtime(ultimo_consumo.fechaCorte).strftime("%d/%m/%Y %H:%M") if ultimo_consumo else "—"



    return JsonResponse({
        'notificaciones': mensajes_data,
        'hora_ultimo': hora_ultimo,
        'grafico': {
            'diario': {
                'consumido': consumo_diario,
                'limite': limite_diario
            },
            'mensual': {
                'consumido': consumo_mensual,
                'umbral': umbral_mensual,
                'base': lectura_base
            }
        }
    })




def estadisticaPresenracion(request, id):

    if not request.session.get('es_usuario'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    
    usuario = get_object_or_404(Usuario, pk=id)
    sensores_asignados = UsuarioSensor.objects.filter(usuario=usuario)

    sensores_con_config = []

    for sensor in sensores_asignados:
        sensores_con_config.append({
            'id': sensor.id,
            'sensor': sensor.sensor,
            'ubicacionSensor': sensor.ubicacionSensor,
        })

    return render(request, 'estadisticas/estaditicaPrevio.html', {
        'sensores': sensores_con_config,
        'usuario_id': usuario.id,
    })



def reporte_consumo_json(request, sensor_id):

    
    historico = ConsumoHistorico.objects.filter(usuarioSensor_id=sensor_id).order_by('fechaPeriodo')

    datos = {
        "fechas": [h.fechaPeriodo.strftime('%d/%m') for h in historico],
        "consumo_total": [h.consumoTotal for h in historico],
        "maximo": [h.maxConsumo for h in historico],
        "promedio": [h.minConsumo for h in historico], 
    }

    return JsonResponse(datos)


def reporte_consumo_pie(request, sensor_id):

    
    historico = (
        ConsumoHistorico.objects
        .filter(usuarioSensor_id=sensor_id)
        .order_by('-fechaPeriodo')[:7]
    )

    historico = list(historico)[::-1]

    dias_en = [h.fechaPeriodo.strftime('%A') for h in historico]
    
    dias_traducidos = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

    dias_es = [dias_traducidos.get(dia, dia) for dia in dias_en]
    consumos = [h.consumoTotal for h in historico]

    return JsonResponse({
        "dias": dias_es,
        "consumos": consumos
    })









def estadisticas_geograficas(request):
    inicio = parse_date(request.GET.get("inicio"))
    fin = parse_date(request.GET.get("fin"))

    historial = ConsumoHistorico.objects.filter(
        fechaPeriodo__range=[inicio, fin]
    ).values(
        "usuarioSensor__sensor__sensorID",
        "usuarioSensor__sensor__nombreSensor",
        "usuarioSensor__sensor__latitud",
        "usuarioSensor__sensor__longitud",
        "usuarioSensor__sensor__fechaInscripcion"  # 🕒 Fecha de inscripción añadida
    ).annotate(
        consumo_total=Sum("consumoTotal")
    )


    return JsonResponse(list(historial), safe=False)




def admin_estadisticas_geograficas(request):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    return render(request, 'Notificaciones/panelEstadisticas.html', {

    })



def admin_estadisticas_geograficas_avanzadas(request):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    return render(request, 'Notificaciones/panelEstadisticasAvanzadas.html', {

    })













def consumo_dinamico_hoy(request):
    # Hora local en UTC-5   



    hora_ecuador = now() - timedelta(hours=5)
    fecha_ec_local = hora_ecuador.date()

    # Ahora convertimos ese día local a rango UTC
    inicio_utc = datetime.combine(fecha_ec_local, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=5)
    fin_utc = inicio_utc + timedelta(days=1)


    

    # Filtro correcto en UTC que representa "hoy" en UTC-5
    registros = ConsumoDinamico.objects.select_related("usuarioSensor__sensor")\
        .filter(fechaCorte__gte=inicio_utc, fechaCorte__lt=fin_utc)\
        .order_by("fechaCorte")



    data = {}
    for r in registros:
        sensor = r.usuarioSensor.sensor
        sid = sensor.sensorID
        if sid not in data:
            data[sid] = {
                "sensorID": sid,
                "nombreSensor": sensor.nombreSensor,
                "latitud": sensor.latitud,
                "longitud": sensor.longitud,
                "fechas": [],
                "valores": []
            }

        # 👇 Ajusta hora UTC a hora local
        local_time = localtime(r.fechaCorte)
        data[sid]["fechas"].append(local_time.strftime("%H:%M"))

        data[sid]["valores"].append(round(r.consumoDinamico, 2))

        


    return JsonResponse(list(data.values()), safe=False)

