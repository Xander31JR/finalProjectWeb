from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone

from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.Sensor.models import Sensor
from Aplicaciones.UsuarioSensor.models import UsuarioSensor

class UsuarioSensorTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Configurar datos de prueba
        self.usuario1 = Usuario.objects.create(
            nombreUsuario="Usuario1",
            correoUsuario="usuario1@test.com",
            passwordUsuario="password123"
        )
        
        self.usuario2 = Usuario.objects.create(
            nombreUsuario="Usuario2",
            correoUsuario="usuario2@test.com",
            passwordUsuario="password456"
        )
        
        self.sensor1 = Sensor.objects.create(
            sensorID=1,
            nombreSensor="Sensor1",
            latitud=-0.74,
            longitud=-78.64
        )
        
        self.sensor2 = Sensor.objects.create(
            sensorID=2,
            nombreSensor="Sensor2",
            latitud=-0.75,
            longitud=-78.65
        )
        
        # Configurar sesión admin
        session = self.client.session
        session['es_admin'] = True
        session.save()

    def test_modelo_usuario_sensor(self):
        """Test para verificar la creación correcta del modelo"""
        asignacion = UsuarioSensor.objects.create(
            usuario=self.usuario1,
            sensor=self.sensor1,
            ubicacionSensor="Ubicación1"
        )
        
        self.assertEqual(asignacion.usuario, self.usuario1)
        self.assertEqual(asignacion.sensor, self.sensor1)
        self.assertEqual(asignacion.ubicacionSensor, "Ubicación1")
        self.assertIsNotNone(asignacion.fechaAsignacion)
        
        # Verificar unique_together
        with self.assertRaises(Exception):
            UsuarioSensor.objects.create(
                usuario=self.usuario1,
                sensor=self.sensor1,
                ubicacionSensor="Ubicación1"
            )

    


 




