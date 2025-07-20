from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone

from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.Sensor.models import Sensor
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from Aplicaciones.consumoDinamico.models import ConsumoDinamico

class ConsumoDinamicoTests(TestCase):
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
        
        # Configurar sesión admin
        session = self.client.session
        session['es_admin'] = True
        session.save()

    def test_modelo_consumo_dinamico(self):
        """Test para verificar la creación correcta del modelo"""
        consumo = ConsumoDinamico.objects.create(
            consumoDinamico=150.75,
            usuarioSensor=self.asignacion
        )
        
        self.assertEqual(consumo.consumoDinamico, 150.75)
        self.assertEqual(consumo.usuarioSensor, self.asignacion)
        self.assertIsNotNone(consumo.fechaCorte)
        self.assertEqual(
            str(consumo), 
            f"{self.asignacion} - {150.75} L at {consumo.fechaCorte}"
        )

    def test_agregar_consumo_dinamico(self):
        """Test para la vista agregar_consumo_dinamico"""
        response = self.client.post(
            reverse('agregar_consumo_dinamico'),
            {
                'consumoDinamico': '200.5',
                'usuarioSensor': self.asignacion.id
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("agregado correctamente" in str(m) for m in messages))
        self.assertTrue(ConsumoDinamico.objects.filter(consumoDinamico=200.5).exists())

    def test_agregar_consumo_dinamico_invalido(self):
        """Test para datos inválidos en agregar_consumo_dinamico"""
        # Test con consumo no numérico
        response = self.client.post(
            reverse('agregar_consumo_dinamico'),
            {
                'consumoDinamico': 'no es un número',
                'usuarioSensor': self.asignacion.id
            },
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("debe ser un número válido" in str(m) for m in messages))

    def test_editar_consumo_dinamico(self):
        """Test para la vista editar_consumo_dinamico"""
        consumo = ConsumoDinamico.objects.create(
            consumoDinamico=100.0,
            usuarioSensor=self.asignacion
        )
        
        response = self.client.post(
            reverse('editar_consumo_dinamico', args=[consumo.id]),
            {
                'consumoDinamico': '150.25'
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        consumo.refresh_from_db()
        self.assertEqual(consumo.consumoDinamico, 150.25)

    def test_eliminar_consumo_dinamico(self):
        """Test para la vista eliminar_consumo_dinamico"""
        consumo = ConsumoDinamico.objects.create(
            consumoDinamico=300.0,
            usuarioSensor=self.asignacion
        )
        
        response = self.client.post(
            reverse('eliminar_consumo_dinamico', args=[consumo.id]),
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ConsumoDinamico.objects.filter(id=consumo.id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("eliminado correctamente" in str(m) for m in messages))