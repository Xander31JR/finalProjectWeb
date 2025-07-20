from django.db import models

# Create your models here.
class Usuario(models.Model):
    nombreUsuario = models.CharField(max_length=100)
    correoUsuario = models.EmailField(max_length=100, unique=True)
    passwordUsuario = models.CharField(max_length=100, default= "")
    telefonoUsuario = models.CharField(max_length=20, default="")
    direccionUsuario = models.CharField(max_length=255, default="")
    fotoPerfil = models.FileField(upload_to='fotos_perfil/', blank=True, null=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    dni = models.CharField(max_length=20, unique=True, null=True, blank=True)


    def __str__(self):
        return self.nombreUsuario
