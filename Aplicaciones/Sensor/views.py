from django.shortcuts import render, redirect
from .models import Sensor
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import ProtectedError
from django.utils import timezone
from django.db import IntegrityError
from shapely.geometry import Point, Polygon


ZONA_VALIDA = Polygon([
    (-78.64182017298604, -0.7364113429470731),
    (-78.64051936532326, -0.7382487038585325),
    (-78.64007797353952, -0.7385284895693702),
    (-78.63954326673161, -0.7399363701292166),
    (-78.63858448695582, -0.7395716827627106),
    (-78.63794954258522, -0.743553567775562),
    (-78.64225290103482, -0.7455735263016952),
    (-78.64289528140279, -0.7436044463933568),
    (-78.64363599034714, -0.7429337389406793),
    (-78.64370210686344, -0.7414971255382983),
    (-78.64373455412628, -0.7401897324232556),
    (-78.6434588784936,  -0.739381818188093),
    (-78.64308957563733, -0.7384243120840294),
    (-78.64282079641366, -0.7378344430874928),
    (-78.6424991686051,  -0.7373829516594358),
    (-78.64182017298604, -0.7364113429470731)
])

def lista_sensor(request):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 

    sensores = Sensor.objects.all() 


    return render(request, 'sensores/index.html', {
        'sensores': sensores,
    })




def agregar_sensor(request):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    
    sensores_existentes = Sensor.objects.values_list('sensorID', flat=True)

    if request.method == 'POST':
        sensorID = request.POST.get('sensorID')
        nombreSensor = request.POST.get('nombreSensor')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')

        try:
            latitud = float(latitud)
            longitud = float(longitud)
        except (TypeError, ValueError):
            messages.error(request, '❌ Coordenadas inválidas.')
            return redirect('agregar_sensor')

        # Verificar si la coordenada está dentro de la zona permitida
        punto = Point(longitud, latitud)
        if not ZONA_VALIDA.contains(punto):
            messages.error(request, '❌ La ubicación seleccionada está fuera de la zona permitida.')
            return redirect('agregar_sensor')

        # Verificar que el sensorID sea único
        if Sensor.objects.filter(sensorID=sensorID).exists():
            messages.error(request, f"❌ Ya existe un medidor con el ID único '{sensorID}'. Usa otro.")
            return redirect('agregar_sensor')

        # Crear el sensor si todo está correcto
        try:
            Sensor.objects.create(
                sensorID=sensorID,
                nombreSensor=nombreSensor,
                latitud=latitud,
                longitud=longitud,
                fechaInscripcion=timezone.now()
            )
            messages.success(request, f"✅ Medidor con Número #{sensorID} registrado correctamente.")
            return redirect('lista_sensor')
        except IntegrityError:
            messages.error(request, "❌ Error al registrar el medidor. Verifica los datos.")

    return render(request, 'sensores/agregar_sensor.html', {
        'sensor_ids': list(sensores_existentes)
    })


def editar_sensor(request, sensorID):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    try:
        sensor = Sensor.objects.get(sensorID=sensorID)
    except Sensor.DoesNotExist:
        messages.error(request, 'Medidor no encontrado.')
        return redirect('lista_sensor')

    if request.method == 'POST':
        sensor.nombreSensor = request.POST.get('nombreSensor')
        lat = request.POST.get('latitud', '').replace(',', '.')
        lng = request.POST.get('longitud', '').replace(',', '.')

        try:
            lat = float(lat)
            lng = float(lng)
            punto = Point(lng, lat)

            if not ZONA_VALIDA.contains(punto):
                messages.error(request, '❌ La ubicación está fuera del área permitida.')
                return redirect('editar_sensor', sensorID=sensorID)

            sensor.latitud = lat
            sensor.longitud = lng
            sensor.save()
            messages.success(request, '✅ Medidor actualizado correctamente.')

        except (TypeError, ValueError):
            messages.error(request, '❌ Las coordenadas no son válidas.')

        return redirect('lista_sensor')

    return render(request, 'sensores/editar_sensor.html', {'sensor': sensor})

def eliminar_sensor(request, sensorID):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    sensores = Sensor.objects.filter(sensorID=sensorID)
    if not sensores.exists():
        messages.error(request, 'Sensor no encontrado.')
        return redirect('lista_sensor')

    sensor = sensores.first()

    try:
        sensor.delete()
        messages.success(request, 'Sensor eliminado correctamente.')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar este medidor porque tiene datos asociados.')

    return redirect('lista_sensor')
