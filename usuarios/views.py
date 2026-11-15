from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from .models import perfil, SolicitudRecuperacion
from django.views.decorators.http import require_POST

from .forms import CrearUsuarioForm, EditarPerfilUsuarioForm, SolicitudRecuperacionForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# Create your views here.

def login_View(request):
    return render(request, 'usuarios/login.html')

def solicitar_recuperacion(request):
    form = SolicitudRecuperacionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Recibimos tu solicitud. El administrador revisará los datos.",
        )
        return redirect("solicitar_recuperacion")

    return render(
        request,
        "usuarios/solicitar_recuperacion.html",
        {"form": form},
    )

@login_required(login_url="login")
def listar_solicitudes_recuperacion(request):
    try:
        rol_usuario = request.user.perfil.rol.nombre
    except AttributeError:
        rol_usuario = None

    if rol_usuario != "Administrador" and not request.user.is_superuser:
        raise PermissionDenied

    solicitudes = SolicitudRecuperacion.objects.all()

    return render(
        request,
        "usuarios/listar_solicitudes_recuperacion.html",
        {"solicitudes": solicitudes},
    )

@login_required(login_url="login")
@require_POST
def resolver_solicitud_recuperacion(request, solicitud_id):
    try:
        rol_usuario = request.user.perfil.rol.nombre
    except AttributeError:
        rol_usuario = None

    if rol_usuario != "Administrador" and not request.user.is_superuser:
        raise PermissionDenied

    solicitud = get_object_or_404(
        SolicitudRecuperacion,
        pk=solicitud_id,
    )

    if solicitud.estado != "pendiente":
        messages.info(request, "Esta solicitud ya fue revisada.")
        return redirect("listar_solicitudes_recuperacion")

    accion = request.POST.get("accion")

    if accion == "aprobar":
        if request.POST.get("confirmacion") != "si":
            messages.error(
                request,
                "Confirma que verificaste la identidad y el correo antes de aprobar.",
            )
            return redirect("listar_solicitudes_recuperacion")
        
        perfil_usuario = (
            perfil.objects
            .select_related("usuario")
            .filter(rut=solicitud.rut)
            .first()
        )

        if not perfil_usuario:
            messages.error(
                request,
                "No se encontró un usuario registrado con ese RUT.",
            )
            return redirect("listar_solicitudes_recuperacion")

        usuario = perfil_usuario.usuario
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        token = default_token_generator.make_token(usuario)

        ruta = reverse(
            "password_reset_confirm",
            kwargs={"uidb64": uid, "token": token},
        )
        enlace = request.build_absolute_uri(ruta)

        send_mail(
            subject="Recuperación de contraseña",
            message=(
                f"Hola {solicitud.nombre_completo},\n\n"
                "El administrador aprobó tu solicitud. "
                "Usa este enlace para crear una contraseña nueva:\n\n"
                f"{enlace}\n\n"
                "Si no solicitaste este cambio, contacta al liceo."
            ),
            from_email=None,
            recipient_list=[solicitud.correo],
            fail_silently=False,
        )

        solicitud.estado = "aprobada"
        solicitud.save(update_fields=["estado"])
        messages.success(
            request,
            "Solicitud aprobada y correo de recuperación generado.",
        )

    elif accion == "rechazar":
        solicitud.estado = "rechazada"
        solicitud.save(update_fields=["estado"])
        messages.success(request, "Solicitud rechazada.")

    return redirect("listar_solicitudes_recuperacion")

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
