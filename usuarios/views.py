from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .forms import CrearUsuarioForm

# Create your views here.

def login_View(request):
    return render(request, 'usuarios/login.html')

@login_required(login_url="login")
def crear_usuario(request):
    try:
        rol_usuario = request.user.perfil.rol.nombre
    except AttributeError:
        rol_usuario = None

    if rol_usuario != "Administrador" and not request.user.is_superuser:
        raise PermissionDenied

    form = CrearUsuarioForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(
            request,
            f"El usuario {usuario.username} fue creado correctamente."
        )
        return redirect("crear_usuario")

    return render(
        request,
        "usuarios/crear_usuario.html",
        {"form": form},
    )
