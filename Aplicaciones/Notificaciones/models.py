from django.db import models
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from Aplicaciones.TipoMensaje.models import TipoMensaje
from django.db.models import PROTECT


class Notificacion(models.Model):
    mensaje = models.TextField()
    fechaEnvio = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    usuarioSensor = models.ForeignKey(UsuarioSensor, on_delete=models.PROTECT)
    tipoMensaje = models.ForeignKey(TipoMensaje, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.usuarioSensor} - {self.tipoMensaje} - {self.fechaEnvio}"
