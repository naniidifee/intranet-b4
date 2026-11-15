from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .data import ESPECIALIDADES_DATA, equipo_data, NOTICIAS_DATA

from .models import Comunicado

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

    return render(request, 'intranet/login.html')


# Diccionario centralizado con la información de cada especialidad

def inicio(request):
    return render(request, 'intranet/index.html')

def especialidad_detail(request, slug):
    # Busca la especialidad en el diccionario o lanza un error 404 si no existe
    esp = ESPECIALIDADES_DATA.get(slug)
    if not esp:
        from django.http import Http404
        raise Http404("Especialidad no encontrada")
        
    context = {
        'esp': esp
    }
    return render(request, 'intranet/especialidades.html', context)

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