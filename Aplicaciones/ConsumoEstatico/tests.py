from django.test import TestCase, Client
from django.urls import reverse
from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.Sensor.models import Sensor
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from Aplicaciones.ConsumoEstatico.models import ConsumoEstatico
from django.contrib.messages import get_messages
from django.utils import timezone

class ConsumoEstaticoTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Configurar sesión como admin
        session = self.client.session
        session['es_admin'] = True
        session.save()
        
        # Crear datos de prueba
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
        
        self.consumo = ConsumoEstatico.objects.create(
            consumoEstatico=100.5,
            usuarioSensor=self.asignacion
        )

    def test_modelo_consumo_estatico_creacion(self):
        """Test para verificar la creación correcta de un consumo estático"""
        consumo = ConsumoEstatico.objects.create(
            consumoEstatico=150.75,
            usuarioSensor=self.asignacion
        )
        
        self.assertEqual(consumo.consumoEstatico, 150.75)
        self.assertEqual(consumo.usuarioSensor, self.asignacion)
        self.assertIsNotNone(consumo.fechaCorte)
        self.assertEqual(str(consumo), f"{self.asignacion} - {150.75} L - {consumo.fechaCorte.date()}")

    def test_agregar_consumo_estatico_view(self):
        """Test para verificar la vista de agregar consumo estático"""
        response = self.client.get(reverse('agregar_consumo_estatico'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('usuariosSensoresDisponibles', response.context)
        
        # Verificar que solo muestra asignaciones sin consumo estático
        self.assertEqual(len(response.context['usuariosSensoresDisponibles']), 0)
        
        # Crear otra asignación sin consumo para probar
        nueva_asignacion = UsuarioSensor.objects.create(
            usuario=self.usuario,
            sensor=self.sensor,
            ubicacionSensor="Otra Ubicación"
        )
        
        response = self.client.get(reverse('agregar_consumo_estatico'))
        self.assertEqual(len(response.context['usuariosSensoresDisponibles']), 1)
        self.assertEqual(response.context['usuariosSensoresDisponibles'][0], nueva_asignacion)

    def test_editar_consumo_estatico_view_get(self):
        """Test para verificar la vista GET de editar consumo estático"""
        response = self.client.get(reverse('editar_consumo_estatico', args=[self.consumo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('consumo', response.context)
        self.assertEqual(response.context['consumo'], self.consumo)

    def test_editar_consumo_estatico_view_post(self):
        """Test para verificar la actualización de consumo estático"""
        response = self.client.post(reverse('editar_consumo_estatico', args=[self.consumo.id]), {
            'consumoEstatico': '200.75'
        }, follow=True)
        
        self.assertRedirects(response, reverse('lista_consumo_estatico'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("actualizado correctamente" in str(m) for m in messages))
        
        self.consumo.refresh_from_db()
        self.assertEqual(self.consumo.consumoEstatico, 200.75)

    def test_editar_consumo_estatico_view_invalid(self):
        """Test para verificar manejo de datos inválidos"""
        response = self.client.post(reverse('editar_consumo_estatico', args=[self.consumo.id]), {
            'consumoEstatico': 'no es un número'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Error al actualizar" in str(m) for m in messages))

    def test_eliminar_consumo_estatico_view(self):
        """Test para verificar la eliminación de consumo estático"""
        consumo_id = self.consumo.id
        response = self.client.get(reverse('eliminar_consumo_estatico', args=[consumo_id]), follow=True)
        
        self.assertRedirects(response, reverse('lista_consumo_estatico'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("eliminado correctamente" in str(m) for m in messages))
        self.assertFalse(ConsumoEstatico.objects.filter(id=consumo_id).exists())

    def test_eliminar_consumo_estatico_view_not_found(self):
        """Test para verificar manejo de consumo no encontrado"""
        response = self.client.get(reverse('eliminar_consumo_estatico', args=[999]), follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("no encontrado" in str(m) for m in messages))