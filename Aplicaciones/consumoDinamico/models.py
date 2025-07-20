from django.db import models
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from django.db.models import PROTECT

# Create your models here.



class ConsumoDinamico(models.Model):
    consumoDinamico = models.FloatField()
    fechaCorte = models.DateTimeField(auto_now_add=True)
    usuarioSensor = models.ForeignKey(UsuarioSensor, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.usuarioSensor} - {self.consumoDinamico} L at {self.fechaCorte}"
