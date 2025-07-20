"""
URL configuration for HydroSys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('controlador/', include('Aplicaciones.ControladorCentral.urls')),
    path('', include('Aplicaciones.PWA.urls')),
    path('usuario/', include('Aplicaciones.Usuario.urls')),
    path('usuarioSensor/', include('Aplicaciones.UsuarioSensor.urls')),  # Incluye las URLs de UsuarioSensor


    path('limiteUsuario/', include('Aplicaciones.LimiteUsuario.urls')),
    path('notificaciones/', include('Aplicaciones.Notificaciones.urls')),
    path('sensores/', include('Aplicaciones.Sensor.urls')),
    path('consumoEstatico/', include('Aplicaciones.ConsumoEstatico.urls')),
    path('consumoHistorico/', include('Aplicaciones.ConsumoHistorico.urls')),
    path('consumoDinamico/', include('Aplicaciones.consumoDinamico.urls')),
    path('logsUsuario/', include('Aplicaciones.LogsUsuario.urls')),
    path('tipoMensaje/', include('Aplicaciones.TipoMensaje.urls')),
    
    



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
