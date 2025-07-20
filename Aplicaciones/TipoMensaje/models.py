from django.db import models


class TipoMensaje(models.Model):
    tipoAlerta = models.CharField(max_length=100)
    mensaje_default = models.TextField()

    def __str__(self):
        return self.tipoAlerta
