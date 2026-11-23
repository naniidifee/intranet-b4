from django.utils.crypto import get_random_string
from .services import enviar_correo_avb


def procesar_recuperacion_usuario(usuario):
    """
    Asigna una contraseña temporal al usuario y le envía la notificación por correo.
    Retorna (ok, mensaje).
    """
    if not usuario.email:
        return False, f"El usuario '{usuario.username}' no tiene correo registrado."

    clave_temporal = get_random_string(length=10)
    usuario.set_password(clave_temporal)
    usuario.save(update_fields=["password"])

    nombre = usuario.get_full_name() or usuario.username
    asunto = "Recuperación de contraseña - Intranet Liceo Antonio Varas de la Barra"
    cuerpo = (
        f"Hola {nombre},\n\n"
        f"Se ha procesado tu solicitud de recuperación de contraseña para la Intranet AVB.\n\n"
        f"Usuario: {usuario.username}\n"
        f"Contraseña temporal: {clave_temporal}\n\n"
        f"Por seguridad, inicia sesión y cambia tu contraseña a la brevedad.\n\n"
        f"Atentamente,\n"
        f"Administración · Liceo Bicentenario Antonio Varas de la Barra"
    )

    return enviar_correo_avb(
        destinatarios=[usuario.email],
        asunto=asunto,
        cuerpo=cuerpo,
    )