from django.test import TestCase, Client
from django.urls import reverse
from .models import Sensor
from django.utils import timezone
from django.contrib.messages import get_messages

class SensorTests(TestCase):

    def setUp(self):
        self.client = Client()
        # Crear usuario admin en sesión para pasar el control de permisos
        session = self.client.session
        session['es_admin'] = True
        session.save()

        # Crear un sensor inicial para pruebas
        self.sensor = Sensor.objects.create(
            sensorID=1,
            nombreSensor="Sensor 1",
            latitud=-0.74,
            longitud=-78.64,
            fechaInscripcion=timezone.now()
        )



    def test_lista_sensor(self):
        response = self.client.get(reverse('lista_sensor'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sensor 1")

    def test_agregar_sensor_get(self):
        response = self.client.get(reverse('agregar_sensor'))
        self.assertEqual(response.status_code, 200)



    def test_agregar_sensor_post_fuera_zona(self):
        data = {
            'sensorID': 3,
            'nombreSensor': 'Sensor Fuera',
            'latitud': '0',    # Coordenadas fuera del polígono
            'longitud': '0',
        }
        response = self.client.post(reverse('agregar_sensor'), data, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("fuera de la zona permitida" in str(m) for m in messages))
        self.assertFalse(Sensor.objects.filter(sensorID=3).exists())

    def test_editar_sensor_get(self):
        response = self.client.get(reverse('editar_sensor', args=[self.sensor.sensorID]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sensor.nombreSensor)

    def test_editar_sensor_post_valido(self):
        data = {
            'nombreSensor': 'Sensor Editado',
            'latitud': str(self.sensor.latitud),
            'longitud': str(self.sensor.longitud),
        }
        response = self.client.post(reverse('editar_sensor', args=[self.sensor.sensorID]), data, follow=True)
        self.assertRedirects(response, reverse('lista_sensor'))
        self.sensor.refresh_from_db()
        self.assertEqual(self.sensor.nombreSensor, 'Sensor Editado')

    def test_editar_sensor_post_fuera_zona(self):
        data = {
            'nombreSensor': 'Sensor Editado',
            'latitud': '0',
            'longitud': '0',
        }
        response = self.client.post(reverse('editar_sensor', args=[self.sensor.sensorID]), data, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("fuera del área permitida" in str(m) for m in messages))
        self.sensor.refresh_from_db()
        self.assertNotEqual(self.sensor.latitud, 0)

    def test_eliminar_sensor(self):
        response = self.client.get(reverse('eliminar_sensor', args=[self.sensor.sensorID]), follow=True)
        self.assertRedirects(response, reverse('lista_sensor'))
        self.assertFalse(Sensor.objects.filter(sensorID=self.sensor.sensorID).exists())

    def test_eliminar_sensor_no_existe(self):
        response = self.client.get(reverse('eliminar_sensor', args=[999]), follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("no encontrado" in str(m).lower() for m in messages))



