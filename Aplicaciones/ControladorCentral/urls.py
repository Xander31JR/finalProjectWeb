from django.urls import path
from .views import recibir_datos_esp32

urlpatterns = [
    path('recibir_datos/', recibir_datos_esp32, name='recibir_datos'),
]