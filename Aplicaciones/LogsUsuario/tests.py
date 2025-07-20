from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import datetime, timedelta

from Aplicaciones.Usuario.models import Usuario
from Aplicaciones.LogsUsuario.models import LogUsuario

class LogUsuarioTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear usuario de prueba
        self.usuario = Usuario.objects.create(
            nombreUsuario="Usuario Test",
            correoUsuario="test@example.com",
            passwordUsuario="testpass123"
        )
        
        # Crear log de prueba
        self.log = LogUsuario.objects.create(
            evento="Inicio de sesión",
            descripcion="El usuario inició sesión correctamente",
            usuario=self.usuario
        )
        
        # Configurar sesión admin
        session = self.client.session
        session['es_admin'] = True
        session.save()

    def test_modelo_log_usuario(self):
        """Test para verificar la creación correcta del modelo"""
        log = LogUsuario.objects.create(
            evento="Prueba",
            descripcion="Descripción de prueba",
            usuario=self.usuario
        )
        
        self.assertEqual(log.evento, "Prueba")
        self.assertEqual(log.descripcion, "Descripción de prueba")
        self.assertEqual(log.usuario, self.usuario)
        self.assertIsNotNone(log.fechaCambio)
        self.assertEqual(str(log), f"{self.usuario} - Prueba")

    def test_agregar_log_usuario(self):
        """Test para la vista agregar_log_usuario"""
        # Datos de prueba
        test_data = {
            'fechaCambio': timezone.now().isoformat(),
            'evento': 'Evento de prueba',
            'descripcion': 'Descripción de prueba',
            'usuario': self.usuario.id
        }
        
        response = self.client.post(
            reverse('agregar_log_usuario'),
            data=test_data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("creado exitosamente" in str(m) for m in messages))
        self.assertTrue(LogUsuario.objects.filter(evento="Evento de prueba").exists())

    def test_agregar_log_usuario_invalido(self):
        """Test para datos inválidos en agregar_log_usuario"""
        # Test con fecha inválida
        response = self.client.post(
            reverse('agregar_log_usuario'),
            data={
                'fechaCambio': 'fecha-invalida',
                'evento': 'Evento',
                'descripcion': 'Descripción',
                'usuario': self.usuario.id
            },
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Formato de fecha inválido" in str(m) for m in messages))

    def test_editar_log_usuario(self):
        """Test para la vista editar_log_usuario"""
        nueva_fecha = (timezone.now() - timedelta(days=1)).isoformat()
        
        response = self.client.post(
            reverse('editar_log_usuario', args=[self.log.id]),
            data={
                'fechaCambio': nueva_fecha,
                'evento': 'Evento actualizado',
                'descripcion': 'Descripción actualizada'
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.log.refresh_from_db()
        self.assertEqual(self.log.evento, "Evento actualizado")
        self.assertEqual(self.log.descripcion, "Descripción actualizada")

    def test_eliminar_log_usuario(self):
        """Test para la vista eliminar_log_usuario"""
        log_id = self.log.id
        response = self.client.post(
            reverse('eliminar_log_usuario', args=[log_id]),
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LogUsuario.objects.filter(id=log_id).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("eliminado correctamente" in str(m) for m in messages))

    def test_eliminar_log_usuario_no_existente(self):
        """Test para eliminar un log que no existe"""
        response = self.client.post(
            reverse('eliminar_log_usuario', args=[9999]),
            follow=True
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("no encontrado" in str(m) for m in messages))