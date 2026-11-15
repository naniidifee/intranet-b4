from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .data import ESPECIALIDADES_DATA, equipo_data, NOTICIAS_DATA


# -------------------------------------------------------------------
# Vistas Públicas e Intranet Base
# -------------------------------------------------------------------

def home(request):
    return render(request, 'intranet/index.html')


def intranet_login(request):
    if request.method == "POST":
        usuario = request.POST.get('username')
        contrasena = request.POST.get('password')
        user = authenticate(request, username=usuario, password=contrasena)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido/a {user.username}')
            return redirect('intranet_dashboard')
        else:
            messages.error(request, 'Credenciales incorrectas. Verifique su usuario y contraseña.')

    return render(request, 'usuarios/login.html')


# Diccionario centralizado con la información de cada especialidad

def inicio(request):
    return render(request, 'intranet/index.html')

def especialidad_detail(request, slug):
    # Busca la especialidad en el diccionario o lanza un error 404 si no existe
    esp = ESPECIALIDADES_DATA.get(slug)
    if not esp:
        raise Http404("Especialidad no encontrada")
    context = {
        'esp': esp
    }
    return render(request, 'intranet/especialidades.html', context)


@login_required(login_url="login")
def intranet_dashboard(request):
    if request.user.is_superuser:
        return render(request, "usuarios/portal_administrador.html")
    try:
        rol = request.user.perfil.rol.nombre
    except AttributeError:
        messages.error(request, "Tu cuenta aún no tiene un rol asignado.")
        return redirect("home")

    if rol == "Administrador":
        return render(request, "usuarios/portal_administrador.html")

    if rol == "Estudiante":
        return redirect("horario_estudiante")

    messages.info(request, "La pantalla de tu rol aún está en preparación.")
    return redirect("home")


def portal_noticias(request):
    context = {
        'noticias': NOTICIAS_DATA
    }
    return render(request, 'intranet/noticias.html', context)

def detalle_noticia(request, noticia_id):
    noticia = NOTICIAS_DATA.get(str(noticia_id))
    if not noticia:
        raise Http404("Noticia no encontrada")
    context = {
        'noticia': noticia
    }
    return render(request, 'intranet/detalle_noticia.html', context)

def equipo_gestion(request):
    return render(request, 'intranet/noticias.html', {'equipo': equipo_data})