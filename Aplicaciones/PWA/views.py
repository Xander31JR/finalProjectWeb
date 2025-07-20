from django.shortcuts import render, redirect
from django.contrib.auth import logout
from Aplicaciones.Notificaciones.models import Notificacion

from Aplicaciones.ConsumoEstatico.models import ConsumoEstatico
from Aplicaciones.ConsumoHistorico.models import ConsumoHistorico
from Aplicaciones.consumoDinamico.models import ConsumoDinamico
from Aplicaciones.LimiteUsuario.models import LimiteUsuario
from Aplicaciones.LogsUsuario.models import LogUsuario
from Aplicaciones.TipoMensaje.models import TipoMensaje
from django.contrib import messages


# Create your views here.
def IniciarSesion(request):
    return render(request, 'iniciarSesion/login.html')

def cerrar_sesion(request):

    request.session.flush()

    logout(request)

    return redirect('login')  




def lista_consumo_estatico(request):

    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    consumos_estaticos = ConsumoEstatico.objects.all()
    return render(request, 'admin/consumo_estatico.html', {
        'consumos_estaticos': consumos_estaticos
    })

def lista_consumo_dinamico(request):

    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    consumos_dinamicos = ConsumoDinamico.objects.all()
    return render(request, 'admin/consumo_dinamico.html', {
        'consumos_dinamicos': consumos_dinamicos
    })

def lista_notificaciones(request):

    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    notificaciones = Notificacion.objects.all()
    return render(request, 'admin/notificaciones.html', {
        'notificaciones': notificaciones
    })

def lista_tipo_mensaje(request):

    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    tipo_mensajes = TipoMensaje.objects.all()

    return render(request, 'admin/tipo_mensajes.html', {
        'tipo_mensajes': tipo_mensajes
    })


def ver_logs_usuario(request):

    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    
    logs = LogUsuario.objects.all().order_by('-fechaCambio')

    return render(request, 'admin/log_usuario.html', {
        'logs': logs
    })

def lista_consumo_historico(request):

    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    
    consumos_historicos = ConsumoHistorico.objects.all()
    return render(request, 'admin/consumo_historico.html', {
        'consumos_historicos': consumos_historicos
    })
