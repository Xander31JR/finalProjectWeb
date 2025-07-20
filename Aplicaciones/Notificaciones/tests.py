from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta, time
from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.Sensor.models import Sensor
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from Aplicaciones.TipoMensaje.models import TipoMensaje
from Aplicaciones.Notificaciones.models import Notificacion
from Aplicaciones.ConsumoHistorico.models import ConsumoHistorico
from Aplicaciones.consumoDinamico.models import ConsumoDinamico
from Aplicaciones.ConsumoEstatico.models import ConsumoEstatico
from Aplicaciones.LimiteUsuario.models import LimiteUsuario

class NotificacionesViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Crear usuario con campos correctos según modelo
        self.usuario = Usuario.objects.create(
            nombreUsuario="Test User",
            correoUsuario="test@example.com",
            passwordUsuario="testpass123",
            telefonoUsuario="0999999999",
            direccionUsuario="Test Address"
        )
        
        # Crear sensor
        self.sensor = Sensor.objects.create(
            sensorID=1,
            nombreSensor="Sensor 1",
            latitud="-0.75",
            longitud="-78.6"
        )
        
        # Crear relación usuario-sensor
        self.usuario_sensor = UsuarioSensor.objects.create(
            usuario=self.usuario,
            sensor=self.sensor,
            ubicacionSensor="Casa"
        )
        
        # Crear tipo de mensaje
        self.tipo_mensaje = TipoMensaje.objects.create(
            tipoAlerta="Consumo",
            mensaje_default="Mensaje por defecto"
        )

        # Crear notificación
        self.notificacion = Notificacion.objects.create(
            mensaje="Mensaje de prueba",
            usuarioSensor=self.usuario_sensor,
            tipoMensaje=self.tipo_mensaje,
            fechaEnvio=make_aware(datetime.now())
        )

        # Configurar sesión
        session = self.client.session
        session['usuario_id'] = self.usuario.id
        session.save()

    def test_obtener_notificaciones_sensor_texto(self):
        url = reverse('obtener_notificaciones_sensor_texto', args=[self.usuario_sensor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('notificaciones', data)
        self.assertGreater(len(data['notificaciones']), 0)
        self.assertEqual(data['notificaciones'][0]['mensaje'], "Mensaje de prueba")

    def test_obtener_notificaciones_sensor_json(self):
        # Configurar datos adicionales necesarios
        LimiteUsuario.objects.create(
            limiteDiario=1500,
            umbralAlerta=10000,
            tiempoMinutos=60,
            usuarioSensor=self.usuario_sensor
        )
        
        ConsumoEstatico.objects.create(
            consumoEstatico=3000,
            usuarioSensor=self.usuario_sensor
        )
        
        ConsumoDinamico.objects.create(
            consumoDinamico=120.5,
            fechaCorte=make_aware(datetime.now()),
            usuarioSensor=self.usuario_sensor
        )

        url = reverse('obtener_notificaciones_sensor', args=[self.usuario_sensor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('grafico', data)
        self.assertIn('diario', data['grafico'])
        self.assertIn('mensual', data['grafico'])
        self.assertIn('notificaciones', data)



    def test_eliminar_notificacion(self):
        url = reverse('eliminar_notificacion', args=[self.notificacion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertFalse(Notificacion.objects.filter(id=self.notificacion.id).exists())

    def test_editar_notificacion_get(self):
        url = reverse('editar_notificacion', args=[self.notificacion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mensaje de prueba')

    def test_editar_notificacion_post(self):
        url = reverse('editar_notificacion', args=[self.notificacion.id])
        response = self.client.post(url, {
            'mensaje': 'Mensaje actualizado',
            'estado': 'on'
        })
        self.assertEqual(response.status_code, 302)
        self.notificacion.refresh_from_db()
        self.assertEqual(self.notificacion.mensaje, 'Mensaje actualizado')
        self.assertTrue(self.notificacion.estado)

    def test_consumo_dinamico_hoy(self):
        # Crear consumo para hoy
        ConsumoDinamico.objects.create(
            consumoDinamico=50.0,
            fechaCorte=make_aware(datetime.now()),
            usuarioSensor=self.usuario_sensor
        )
        
        url = reverse('consumo-dinamico-hoy')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:  # Si hay datos
            self.assertIn('sensorID', data[0])
            self.assertEqual(data[0]['nombreSensor'], 'Sensor 1')

    def test_reporte_consumo_json(self):
        # Crear dato histórico
        ConsumoHistorico.objects.create(
            usuarioSensor=self.usuario_sensor,
            fechaPeriodo=now().date(),
            consumoTotal=500.0,
            maxConsumo=300.0,
            minConsumo=100.0
        )
        
        url = reverse('reporte_consumo_json', args=[self.usuario_sensor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('fechas', data)
        self.assertIn('consumo_total', data)
        self.assertEqual(len(data['fechas']), 1)

    def test_reporte_consumo_pie(self):
        # Crear dato histórico
        ConsumoHistorico.objects.create(
            usuarioSensor=self.usuario_sensor,
            fechaPeriodo=now().date(),
            consumoTotal=500.0,
            maxConsumo=300.0,
            minConsumo=100.0
        )
        
        url = reverse('reporte_consumo_pie', args=[self.usuario_sensor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('dias', data)
        self.assertIn('consumos', data)
        self.assertEqual(len(data['dias']), 1)

    def test_estadisticas_geograficas_json(self):
        # Crear dato histórico
        fecha_actual = now().date()
        ConsumoHistorico.objects.create(
            usuarioSensor=self.usuario_sensor,
            fechaPeriodo=fecha_actual,
            consumoTotal=300.0,
            maxConsumo=200.0,
            minConsumo=100.0
        )
        
        url = reverse('estadisticas_geograficas')
        response = self.client.get(url, {
            'inicio': fecha_actual.isoformat(),
            'fin': fecha_actual.isoformat()
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:  # Si hay datos
            self.assertEqual(data[0]['usuarioSensor__sensor__sensorID'], 1)


