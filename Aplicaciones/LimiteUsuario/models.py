from django.db import models
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from django.db.models import PROTECT


class LimiteUsuario(models.Model):
    limiteDiario = models.FloatField()
    umbralAlerta = models.FloatField()
    tiempoMinutos = models.IntegerField(blank=True)
    fechaCambio = models.DateTimeField(auto_now_add=True)
    usuarioSensor = models.ForeignKey(UsuarioSensor, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.usuarioSensor} - Límite: {self.limiteDiario} L / Cada {self.tiempoMinutos} min"
