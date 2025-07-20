from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario
from django.contrib.auth.hashers import make_password

class UsuarioTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_usuario = Usuario.objects.create(
            nombreUsuario="admin",
            correoUsuario="admin@example.com",
            passwordUsuario=make_password("1234"),
        )
        # Simular sesión admin para tests
        session = self.client.session
        session['es_admin'] = True
        session.save()

    def test_lista_usuario_admin(self):
        response = self.client.get(reverse('lista_usuario'))
        self.assertEqual(response.status_code, 200)

    def test_agregar_usuario(self):
        response = self.client.post(reverse('agregar_usuario'), {
            'correo': 'nuevo@example.com',
            'nombre': 'Nuevo Usuario',
            'telefono': '0999999999',
            'direccion': 'Quito',
        })
        self.assertRedirects(response, reverse('lista_usuario'))

    def test_editar_usuario(self):
        usuario = Usuario.objects.create(
            nombreUsuario="UsuarioTest",
            correoUsuario="testuser@example.com",
            passwordUsuario=make_password("1234"),
        )
        response = self.client.post(reverse('editar_usuario', args=[usuario.id]), {
            'correo': 'editado@example.com',
            'nombre': 'Usuario Editado',
            'telefono': '0987654321',
            'direccion': 'Latacunga',
            'password': 'nuevopass',
        })
        self.assertRedirects(response, reverse('lista_usuario'))

    def test_eliminar_usuario(self):
        usuario = Usuario.objects.create(
            nombreUsuario="UsuarioEliminar",
            correoUsuario="elim@example.com",
            passwordUsuario=make_password("1234"),
        )
        response = self.client.get(reverse('eliminar_usuario', args=[usuario.id]))
        self.assertRedirects(response, reverse('lista_usuario'))