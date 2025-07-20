from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from Aplicaciones.UsuarioSensor.models import UsuarioSensor
from Aplicaciones.consumoDinamico.models import ConsumoDinamico
from Aplicaciones.ConsumoHistorico.models import ConsumoHistorico

class Command(BaseCommand):
    help = "Calcula el consumo diario por sensor y guarda el histórico (total, máximo y promedio sin ceros)"

    def handle(self, *args, **kwargs):
        hoy = timezone.localdate()
        ayer = hoy - timedelta(days=1)

        inicio = timezone.make_aware(datetime.combine(ayer, datetime.min.time()))
        fin = timezone.make_aware(datetime.combine(ayer, datetime.max.time()))

        for sensor in UsuarioSensor.objects.all():
            consumos = ConsumoDinamico.objects.filter(
                usuarioSensor=sensor,
                fechaCorte__range=(inicio, fin),
                consumoDinamico__gt=0  # ⚠️ Solo mayores a cero
            )

            if consumos.exists():
                total = sum(c.consumoDinamico for c in consumos)
                maximo = max(c.consumoDinamico for c in consumos)
                promedio = total / consumos.count()

                ConsumoHistorico.objects.create(
                    consumoTotal=total,
                    maxConsumo=maximo,
                    minConsumo=promedio,  # Aquí guardamos el promedio sin ceros
                    fechaPeriodo=ayer,
                    usuarioSensor=sensor
                )

                self.stdout.write(f"✅ Histórico registrado para {sensor} ({ayer})")
            else:
                self.stdout.write(f"⚠️ No hay datos válidos (>0 L) para {sensor} en {ayer}")
