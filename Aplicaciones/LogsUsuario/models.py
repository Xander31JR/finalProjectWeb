from django.db import models
from Aplicaciones.Usuario.models import Usuario



class LogUsuario(models.Model):
    evento = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    fechaCambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario} - {self.evento}"
