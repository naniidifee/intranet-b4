from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from .models import RegistroEnvioCorreo


def _correos_enviados_hoy():
    hoy = timezone.localdate()
    return RegistroEnvioCorreo.objects.filter(
        enviado_en__date=hoy,
        exitoso=True,
    ).count()


def enviar_correo_avb(destinatarios, asunto, cuerpo, html=None):
    """
    Envía un correo usando la configuración de Gmail definida en settings.py
    y valida el límite diario configurado en CORREO_LIMITE_DIARIO.
    """
    if isinstance(destinatarios, str):
        lista_destinatarios = [destinatarios]
    else:
        lista_destinatarios = [d for d in destinatarios if d]

    if not lista_destinatarios:
        return False, "No hay destinatarios válidos."

    limite = getattr(settings, "CORREO_LIMITE_DIARIO", 500)
    enviados_hoy = _correos_enviados_hoy()
    if enviados_hoy + len(lista_destinatarios) > limite:
        return False, f"Se alcanzó el límite diario de correos ({limite})."

    responder_a = getattr(settings, "CORREO_RESPONDER_A", "")
    headers = {"Reply-To": responder_a} if responder_a else {}

    mensaje = EmailMessage(
        subject=asunto,
        body=cuerpo,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=lista_destinatarios,
        headers=headers,
    )

    if html:
        mensaje.content_subtype = "html"
        mensaje.body = html

    try:
        mensaje.send(fail_silently=False)
        for dest in lista_destinatarios:
            RegistroEnvioCorreo.objects.create(
                destinatario=dest,
                asunto=asunto,
                exitoso=True,
            )
        return True, "Correo enviado correctamente."
    except Exception as exc:
        for dest in lista_destinatarios:
            RegistroEnvioCorreo.objects.create(
                destinatario=dest,
                asunto=asunto,
                exitoso=False,
                error=str(exc)[:500],
            )
        return False, f"Error al enviar correo: {exc}"