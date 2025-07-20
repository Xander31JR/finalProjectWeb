from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .models import Usuario
import uuid
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
import random
from django.db.models import ProtectedError
from django.core.files.storage import default_storage
import os
from Aplicaciones.LogsUsuario.models import LogUsuario
from django.conf import settings
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Create your views here.




def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correoUsuario')
        password = request.POST.get('passwordUsuario')

        if correo == 'mainadmin@main.net' and password == '.net@mainadmin':
            request.session['es_admin'] = True
            return redirect('listaAsignacion')

        try:
            usuario = Usuario.objects.get(correoUsuario=correo)

            if usuario.passwordUsuario == "":
                request.session['pendiente_password'] = usuario.id
                return render(request, 'iniciarSesion/login.html', {
                    'mostrar_modal': True,
                    'usuario_id': usuario.id
                })

            if check_password(password, usuario.passwordUsuario):
                request.session['es_usuario'] = True
                request.session['usuario_id'] = usuario.id
                nombre_usuario = usuario.nombreUsuario

                LogUsuario.objects.create(
                    evento='Inicio de sesión',
                    descripcion=f'El usuario {nombre_usuario} inició sesión correctamente.',
                    usuario=usuario
                )

                return render(request, 'Usuario/menucentral.html', {
                    'usuario_id': usuario.id,
                    'nombre_usuario': nombre_usuario
                })

            else:
                messages.error(request, 'Contraseña incorrecta')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')

    return render(request, 'iniciarSesion/login.html')





def establecer_password(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        nueva_pass = request.POST.get('nueva_password')

        try:
            usuario = Usuario.objects.get(id=usuario_id)
            usuario.passwordUsuario = make_password(nueva_pass)
            usuario.save()

            LogUsuario.objects.create(
                evento='Inicio de sesión',
                descripcion=f'El usuario {usuario.nombreUsuario} configuró su contraseña e inició sesión.',
                usuario=usuario
            )

            messages.success(request, 'Contraseña configurada correctamente.')
            request.session['usuario_id'] = usuario.id
            return render(request, 'Usuario/menucentral.html', {
                'usuario_id': usuario.id,
                'nombre_usuario': usuario.nombreUsuario
            })
        except Usuario.DoesNotExist:
            messages.error(request, 'Error al configurar contraseña.')
            return redirect('login')




def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombreUsuario').strip()
        correo = request.POST.get('correoUsuario').strip().lower()
        password = request.POST.get('passwordUsuario').strip()
        telefono = request.POST.get('telefonoUsuario', '').strip()
        direccion = request.POST.get('direccionUsuario', '').strip()
        dni = request.POST.get('dni', '').strip()
        foto = request.FILES.get('fotoPerfil')

        # Validaciones anticipadas
        if Usuario.objects.filter(telefonoUsuario=telefono).exists():
            messages.error(request, '⚠️ Este número de teléfono ya está registrado.')
            return render(request, 'iniciarSesion/login.html', {'show_register': True})

        if dni and Usuario.objects.filter(dni=dni).exists():
            messages.error(request, '⚠️ Ya existe un usuario con ese número de cédula.')
            return render(request, 'iniciarSesion/login.html', {'show_register': True})

        nombre_temporal = ""
        if foto:
            nombre_temporal = f"{uuid.uuid4().hex}_{foto.name}"
            ruta_temp = os.path.join(settings.MEDIA_ROOT, 'temp', nombre_temporal)
            os.makedirs(os.path.dirname(ruta_temp), exist_ok=True)

            with open(ruta_temp, 'wb+') as destino:
                for chunk in foto.chunks():
                    destino.write(chunk)

        # Código de verificación
        verification_code = random.randint(100000, 999999)


        html_content = render_to_string('emails/confirmacion.html', {
            'codigo': verification_code,
            'nombre': nombre  # si tienes el nombre en sesión
        })

        mensaje = EmailMultiAlternatives(
            subject='Verifica tu cuenta',
            body=f'Tu código de verificación es: {verification_code}',  # texto plano por compatibilidad
            from_email='tu_correo@example.com',
            to=[correo]
        )

        mensaje.attach_alternative(html_content, "text/html")
        mensaje.send()




        # Guardar en sesión para usar después
        request.session['verification_code'] = verification_code
        request.session['correo'] = correo
        request.session['password'] = password
        request.session['nombre'] = nombre
        request.session['telefono'] = telefono
        request.session['direccion'] = direccion
        request.session['dni'] = dni
        request.session['foto_temp'] = nombre_temporal

        messages.success(request, 'Se ha enviado un código de verificación a tu correo electrónico.')
        return redirect('verify_email')

    return render(request, 'iniciarSesion/login.html', {'show_register': True})






def verify_email(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('verification_code')
        codigo_enviado = str(request.session.get('verification_code'))

        if codigo_ingresado == codigo_enviado:
            correo = request.session.get('correo')
            password = request.session.get('password')
            nombre = request.session.get('nombre')
            telefono = request.session.get('telefono')
            direccion = request.session.get('direccion')
            dni = request.session.get('dni')
            nombre_foto = request.session.get('foto_temp')

            if not Usuario.objects.filter(correoUsuario=correo).exists():
                usuario = Usuario(
                    nombreUsuario=nombre,
                    correoUsuario=correo,
                    passwordUsuario=make_password(password),
                    telefonoUsuario=telefono,
                    direccionUsuario=direccion,
                    dni=dni if dni else None
                )

                # Manejo de imagen
                if nombre_foto:
                    ruta_temp = os.path.join(settings.MEDIA_ROOT, 'temp', nombre_foto)
                    if os.path.exists(ruta_temp):
                        with open(ruta_temp, 'rb') as f:
                            usuario.fotoPerfil.save(nombre_foto, f, save=False)
                        os.remove(ruta_temp)

                usuario.save()
                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            else:
                messages.info(request, 'El usuario ya existe. Inicia sesión.')

            # Limpieza opcional de sesión
            for campo in ['verification_code', 'correo', 'password', 'nombre', 'telefono', 'direccion', 'dni', 'foto_temp']:
                request.session.pop(campo, None)

            return redirect('login')
        else:
            messages.error(request, 'Código de verificación incorrecto. Intenta de nuevo.')

    return render(request, 'iniciarSesion/verify.html')

# no tocar
def perfil_usuario(request):
    return render(request, 'Usuario/perfil.html')


    
def menuCentral(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        request.session['usuario_id'] = usuario_id
    else:
        usuario_id = request.session.get('usuario_id')
    
    nombre_usuario = None
    if usuario_id:
        try:
            nombre_usuario = Usuario.objects.get(id=usuario_id).nombreUsuario
        except Usuario.DoesNotExist:
            pass
    print (nombre_usuario)
    
    return render(request, 'Usuario/menucentral.html', {
        'usuario_id': usuario_id,
        'nombre_usuario': nombre_usuario
    })




def lista_usuario(request):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 

    usuarios = Usuario.objects.all()  

    return render(request, 'Usuario/index.html', {
        'usuarios': usuarios,

    })




def agregar_usuario(request):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login')

    correos_existentes = list(Usuario.objects.values_list('correoUsuario', flat=True))
    telefonos_existentes = list(Usuario.objects.values_list('telefonoUsuario', flat=True))
    dni_existentes = list(Usuario.objects.exclude(dni__isnull=True).exclude(dni="").values_list('dni', flat=True))




    if request.method == 'POST':
        correo = request.POST.get('correo')
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono', '')
        direccion = request.POST.get('direccion', '')
        foto = request.FILES.get('fotoPerfil') 
        dni = request.POST.get('dni') 


        if correo in correos_existentes:
            messages.error(request, 'Ya existe un usuario con ese correo.')
            return render(request, 'Usuario/agregar_usuario.html', {
                'correos': correos_existentes,
                'correo': correo,
                'nombre': nombre,
                'telefono': telefono,
                'direccion': direccion,
                'dni':dni
            })
        
        if telefono in telefonos_existentes:
            messages.error(request, 'Ya existe un usuario con ese correo.')
            return render(request, 'Usuario/agregar_usuario.html', {
                'correos': correos_existentes,
                'correo': correo,
                'nombre': nombre,
                'telefono': telefono,
                'direccion': direccion,
                'dni':dni

            })

        if dni in dni_existentes and dni != "":
            messages.error(request, 'Ya existe un usuario con ese DNI.')
            return render(request, 'Usuario/agregar_usuario.html', {
                'correos': correos_existentes,
                'telefonos': telefonos_existentes,
                'dni': dni_existentes,
                'correo': correo,
                'nombre': nombre,
                'telefono': telefono,
                'direccion': direccion,
                'dni_actual': dni
            })


        Usuario.objects.create(
            nombreUsuario=nombre,
            correoUsuario=correo,
            telefonoUsuario=telefono,
            direccionUsuario=direccion,
            dni=dni,
            passwordUsuario="",
            fotoPerfil=foto
        )

        messages.success(request, 'Usuario registrado correctamente.')
        return redirect('lista_usuario')
    

    return render(request, 'Usuario/agregar_usuario.html', {
        'correos': correos_existentes,
        'telefonos': telefonos_existentes,
        'dni': dni_existentes
    })




def editar_usuario(request, usuario_id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 

    usuario = get_object_or_404(Usuario, id=usuario_id)

    correos_existentes = list(Usuario.objects.values_list('correoUsuario', flat=True))
    telefonos_existentes = list(Usuario.objects.values_list('telefonoUsuario', flat=True))
    dni_existentes = list(
        Usuario.objects.exclude(dni__isnull=True).exclude(dni="").values_list('dni', flat=True)
    )

    if request.method == 'POST':
        correo = request.POST.get('correo').strip().lower()
        nombre = request.POST.get('nombre').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        dni = request.POST.get('dni', '').strip()
        password = request.POST.get('password')
        eliminar = request.POST.get('eliminar_password')
        nueva_foto = request.FILES.get('fotoPerfil')

        if Usuario.objects.filter(correoUsuario=correo).exclude(id=usuario_id).exists():
            messages.error(request, 'Ya existe un usuario con ese correo.')
            return render(request, 'Usuario/editar_usuario.html', {
                'usuario': usuario,
                'correo': correo,
                'nombre': nombre,
                'telefono': telefono,
                'direccion': direccion,
                'dni': dni,
                'correo_actual': usuario.correoUsuario,
                'telefono_actual': usuario.telefonoUsuario,
                'dni_actual': usuario.dni or "",
                'correos': correos_existentes,
                'telefonos': telefonos_existentes,
                'dnis': dni_existentes
            })

        if Usuario.objects.filter(telefonoUsuario=telefono).exclude(id=usuario.id).exclude(dni__isnull=True).exclude(dni="").exists():
            messages.error(request, 'Ya existe un usuario con ese número de teléfono.')
            return render(request, 'Usuario/editar_usuario.html', {
                'usuario': usuario,
                'correo': correo,
                'nombre': nombre,
                'telefono': telefono,
                'direccion': direccion,
                'dni': dni,
                'correo_actual': usuario.correoUsuario,
                'telefono_actual': usuario.telefonoUsuario,
                'dni_actual': usuario.dni or "",
                'correos': correos_existentes,
                'telefonos': telefonos_existentes,
                'dnis': dni_existentes
            })

        if dni and Usuario.objects.filter(dni=dni).exclude(id=usuario_id).exists():
            messages.error(request, 'Ya existe un usuario con ese número de cédula.')
            return render(request, 'Usuario/editar_usuario.html', {
                'usuario': usuario,
                'correo': correo,
                'nombre': nombre,
                'telefono': telefono,
                'direccion': direccion,
                'dni': dni,
                'correo_actual': usuario.correoUsuario,
                'telefono_actual': usuario.telefonoUsuario,
                'dni_actual': usuario.dni or "",
                'correos': correos_existentes,
                'telefonos': telefonos_existentes,
                'dnis': dni_existentes
            })

        usuario.correoUsuario = correo
        usuario.nombreUsuario = nombre
        usuario.telefonoUsuario = telefono
        usuario.direccionUsuario = direccion
        usuario.dni = dni if dni else None

        if eliminar == 'true':
            usuario.passwordUsuario = ""
        elif password:
            usuario.passwordUsuario = make_password(password)

        if nueva_foto:
            if usuario.fotoPerfil and default_storage.exists(usuario.fotoPerfil.name):
                default_storage.delete(usuario.fotoPerfil.name)
            usuario.fotoPerfil = nueva_foto

        usuario.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('lista_usuario')

    return render(request, 'Usuario/editar_usuario.html', {
        'usuario': usuario,
        'correo_actual': usuario.correoUsuario,
        'telefono_actual': usuario.telefonoUsuario,
        'dni_actual': usuario.dni or "",
        'correos': correos_existentes,
        'telefonos': telefonos_existentes,
        'dnis': dni_existentes
    })



def eliminar_usuario(request, usuario_id):
    if not request.session.get('es_admin'):
        messages.error(request, 'Ruta protegida, primero debe iniciar sesión.')
        return redirect('login') 
    usuario = get_object_or_404(Usuario, id=usuario_id)

    try:
        usuario.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
    except ProtectedError:
        usuario = Usuario.objects.get(id=usuario_id)
        for rel in usuario._meta.related_objects:
            print(f"{rel.name} → {rel.related_model.__name__} (on_delete={rel.on_delete})")
        messages.error(request, 'No se puede eliminar este usuario porque tiene datos asociados.')

    return redirect('lista_usuario')