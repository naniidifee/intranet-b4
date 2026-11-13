from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .data import ESPECIALIDADES_DATA

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
    """Vista dinámica que carga los datos según la especialidad seleccionada."""
    esp = ESPECIALIDADES_DATA.get(slug)
    if not esp:
        return render(request, '404.html', status=404)
    return render(request, 'intranet/especialidades.html', {'esp': esp})
