from django.test import TestCase, Client
from django.urls import reverse
from .models import ConsumoHistorico
from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.Sensor.models import Sensor
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from django.contrib.messages import get_messages
import datetime

class ConsumoHistoricoCRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear Usuario con campos exactos del modelo real
        self.usuario = Usuario.objects.create(
            nombreUsuario="TestUser",
            correoUsuario="test@example.com",
            passwordUsuario="testpass123",
            telefonoUsuario="1234567890",
            direccionUsuario="Test Address"
        )
        
        # Crear Sensor con campos exactos del modelo real
        self.sensor = Sensor.objects.create(
            sensorID=1,
            nombreSensor="TestSensor",
            latitud=19.4326,
            longitud=-99.1332
        )
        
        # Crear UsuarioSensor válido
        self.usuario_sensor = UsuarioSensor.objects.create(
            usuario=self.usuario,
            sensor=self.sensor,
            ubicacionSensor="Test Location"
        )
        
        # Crear ConsumoHistorico de prueba
        self.consumo = ConsumoHistorico.objects.create(
            consumoTotal=100.0,
            maxConsumo=150.0,
            minConsumo=50.0,
            fechaPeriodo=datetime.date.today(),
            usuarioSensor=self.usuario_sensor
        )
        
        # URLs para las pruebas
        self.agregar_url = reverse('agregar_consumo_historico')
        self.editar_url = reverse('editar_consumo_historico', args=[self.consumo.id])
        self.eliminar_url = reverse('eliminar_consumo_historico', args=[self.consumo.id])

    def test_agregar_consumo_historico(self):
        data = {
            'consumoTotal': '200.0',
            'maxConsumo': '250.0',
            'minConsumo': '150.0',
            'fechaPeriodo': '2023-01-01',
            'usuarioSensor': self.usuario_sensor.id
        }
        
        response = self.client.post(self.agregar_url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ConsumoHistorico.objects.count(), 2)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Consumo histórico agregado correctamente.')



    def test_agregar_consumo_invalido(self):
        data = {
            'consumoTotal': 'no es un número',
            'maxConsumo': '250.0',
            'minConsumo': '150.0',
            'fechaPeriodo': '2023-01-01',
            'usuarioSensor': self.usuario_sensor.id
        }
        
        response = self.client.post(self.agregar_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error', status_code=200)
        self.assertEqual(ConsumoHistorico.objects.count(), 1)