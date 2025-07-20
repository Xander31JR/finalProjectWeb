from django.db import models

class Sensor(models.Model):
    sensorID = models.IntegerField(primary_key=True)
    nombreSensor = models.CharField(max_length=100)
    fechaInscripcion = models.DateTimeField(auto_now_add=True)
    latitud = models.FloatField(default=0.0)
    longitud = models.FloatField(default=0.0)

    def __str__(self):
        return self.nombreSensor
