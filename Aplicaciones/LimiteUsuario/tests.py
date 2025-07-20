from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
import json
from unittest.mock import patch

from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.Sensor.models import Sensor
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from Aplicaciones.LimiteUsuario.models import LimiteUsuario
from Aplicaciones.ConsumoEstatico.models import ConsumoEstatico
from Aplicaciones.consumoDinamico.models import ConsumoDinamico

class LimiteUsuarioTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Configurar datos de prueba
        self.usuario = Usuario.objects.create(
            nombreUsuario="Usuario Test",
            correoUsuario="test@example.com",
            passwordUsuario="password123"
        )
        
        self.sensor = Sensor.objects.create(
            sensorID=1,
            nombreSensor="Sensor Test",
            latitud=-0.74,
            longitud=-78.64
        )
        
        self.asignacion = UsuarioSensor.objects.create(
            usuario=self.usuario,
            sensor=self.sensor,
            ubicacionSensor="Ubicación Test"
        )
        
        self.consumo_estatico = ConsumoEstatico.objects.create(
            usuarioSensor=self.asignacion,
            consumoEstatico=100.5,
            fechaCorte=timezone.now()
        )
        
        self.limite = LimiteUsuario.objects.create(
            usuarioSensor=self.asignacion,
            limiteDiario=150.0,
            umbralAlerta=120.0,
            tiempoMinutos=60
        )
        
        # Configurar sesión de usuario
        session = self.client.session
        session['usuario_id'] = self.usuario.id
        session.save()

    def setUpAdmin(self):
        """Configura sesión como administrador"""
        session = self.client.session
        session['es_admin'] = True
        session.save()

    def test_eliminar_usuario_sensor(self):
        """Test para la vista eliminar_usuario_sensor"""
        response = self.client.get(
            reverse('eliminar_usuario_sensor', args=[self.asignacion.id]),
            follow=True
        )
        
        self.assertRedirects(response, reverse('presentar_limite_usuario', args=[self.usuario.id]))
        self.assertFalse(UsuarioSensor.objects.filter(id=self.asignacion.id).exists())

    from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
import json
from unittest.mock import patch

from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.Sensor.models import Sensor
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from Aplicaciones.LimiteUsuario.models import LimiteUsuario
from Aplicaciones.ConsumoEstatico.models import ConsumoEstatico
from Aplicaciones.consumoDinamico.models import ConsumoDinamico

class LimiteUsuarioTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Configurar datos de prueba
        self.usuario = Usuario.objects.create(
            nombreUsuario="Usuario Test",
            correoUsuario="test@example.com",
            passwordUsuario="password123"
        )
        
        self.sensor = Sensor.objects.create(
            sensorID=1,
            nombreSensor="Sensor Test",
            latitud=-0.74,
            longitud=-78.64
        )
        
        self.asignacion = UsuarioSensor.objects.create(
            usuario=self.usuario,
            sensor=self.sensor,
            ubicacionSensor="Ubicación Test"
        )
        
        self.consumo_estatico = ConsumoEstatico.objects.create(
            usuarioSensor=self.asignacion,
            consumoEstatico=100.5,
            fechaCorte=timezone.now()
        )
        
        self.limite = LimiteUsuario.objects.create(
            usuarioSensor=self.asignacion,
            limiteDiario=150.0,
            umbralAlerta=120.0,
            tiempoMinutos=60
        )
        
        # Configurar sesión de usuario
        session = self.client.session
        session['usuario_id'] = self.usuario.id
        session.save()

    def setUpAdmin(self):
        """Configura sesión como administrador"""
        session = self.client.session
        session['es_admin'] = True
        session.save()

    def test_eliminar_usuario_sensor(self):
        """Test para la vista eliminar_usuario_sensor"""
        response = self.client.get(
            reverse('eliminar_usuario_sensor', args=[self.asignacion.id]),
            follow=True
        )
        
        self.assertRedirects(response, reverse('presentar_limite_usuario', args=[self.usuario.id]))
        self.assertFalse(UsuarioSensor.objects.filter(id=self.asignacion.id).exists())

    def test_crear_nuevo_usuario_sensor(self):
        """Test para crear nueva asignación usuario-sensor"""
        nuevo_sensor = Sensor.objects.create(
            sensorID=2,
            nombreSensor="Nuevo Sensor",
            latitud=-0.75,
            longitud=-78.65
        )
        
        response = self.client.post(
            reverse('crearNuevoUsuarioSesor', args=[self.usuario.id]),
            {
                'sensor_id': '2',
                'ubicacion': 'Nueva Ubicación',
                'medicionBase': '200.5',
                'limiteDiario': '250.0',
                'umbralAlerta': '200.0',
                'tiempo': '30'
            },
            follow=True
        )
        
        self.assertRedirects(response, reverse('presentar_limite_usuario', args=[self.usuario.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("asignado correctamente" in str(m) for m in messages))
        
        # Verificar creación en la base de datos
        self.assertTrue(UsuarioSensor.objects.filter(sensor=nuevo_sensor).exists())
        self.assertTrue(ConsumoEstatico.objects.filter(consumoEstatico=200.5).exists())
        self.assertTrue(LimiteUsuario.objects.filter(limiteDiario=250.0).exists())

    def test_editar_usuario_sensor(self):
        """Test para editar asignación existente"""
        response = self.client.post(
            reverse('editarUsuarioSensor', args=[self.asignacion.id]),
            {
                'ubicacion': 'Ubicación Actualizada',
                'medicionBase': '150.75',
                'limiteDiario': '180.0',
                'umbralAlerta': '140.0',
                'tiempo': '45'
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar actualizaciones
        self.asignacion.refresh_from_db()
        self.limite.refresh_from_db()
        
        self.assertEqual(self.asignacion.ubicacionSensor, 'Ubicación Actualizada')
        self.assertEqual(self.limite.limiteDiario, 180.0)
        self.assertEqual(self.limite.umbralAlerta, 140.0)
        self.assertEqual(self.limite.tiempoMinutos, 45)