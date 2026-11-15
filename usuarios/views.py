from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from .models import perfil
from django.views.decorators.http import require_POST

from .forms import CrearUsuarioForm, EditarPerfilUsuarioForm

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

@login_required(login_url="login")
def listar_usuarios(request):
    try:
        rol_usuario = request.user.perfil.rol.nombre
    except AttributeError:
        rol_usuario = None

    if rol_usuario != "Administrador" and not request.user.is_superuser:
        raise PermissionDenied

    perfiles = (
        perfil.objects
        .select_related("usuario", "rol")
        .order_by("nombre_completo")
    )

    return render(
        request,
        "usuarios/listar_usuarios.html",
        {"perfiles": perfiles},
    )

@login_required(login_url="login")
def editar_usuario(request, usuario_id):
    try:
        rol_usuario = request.user.perfil.rol.nombre
    except AttributeError:
        rol_usuario = None

    if rol_usuario != "Administrador" and not request.user.is_superuser:
        raise PermissionDenied

    perfil_obj = get_object_or_404(
        perfil.objects.select_related("usuario", "rol"),
        usuario_id=usuario_id,
    )

    form = EditarPerfilUsuarioForm(
        request.POST or None,
        instance=perfil_obj,
    )

    if request.method == "POST" and form.is_valid():
        perfil_actualizado = form.save()
        usuario = perfil_actualizado.usuario
        usuario.is_staff = (
            usuario.is_superuser
            or perfil_actualizado.rol.nombre == "Administrador"
        )
        usuario.save(update_fields=["is_staff"])

        messages.success(request, "Los datos del usuario se actualizaron.")
        return redirect("listar_usuarios")

    return render(
        request,
        "usuarios/editar_usuario.html",
        {"form": form, "perfil": perfil_obj},
    )

@login_required(login_url="login")
@require_POST
def cambiar_estado_usuario(request, usuario_id):
    try:
        rol_usuario = request.user.perfil.rol.nombre
    except AttributeError:
        rol_usuario = None

    if rol_usuario != "Administrador" and not request.user.is_superuser:
        raise PermissionDenied

    perfil_obj = get_object_or_404(perfil, usuario_id=usuario_id)
    usuario = perfil_obj.usuario

    if usuario.pk == request.user.pk:
        messages.error(request, "No puedes desactivar tu propia cuenta.")
        return redirect("listar_usuarios")

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])

    return redirect("listar_usuarios")