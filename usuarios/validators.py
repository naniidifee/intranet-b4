import re

from django.core.exceptions import ValidationError

# Sin puntos, con guion y dígito verificador. Ejemplo: 12345678-5
PATRON_RUT_HTML = r"[1-9][0-9]{6,7}-[0-9kK]"
MENSAJE_FORMATO_RUT = (
    "Ingresa el RUT sin puntos y con guion. Ejemplo: 12345678-5."
)


def _digito_verificador(cuerpo):
    suma = 0
    multiplicador = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = 11 - (suma % 11)

    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def validar_rut(valor):
    """Valida un RUT chileno y lo devuelve normalizado (con K en mayúscula)."""
    rut = (valor or "").strip().upper()

    if not re.fullmatch(r"[1-9]\d{6,7}-[\dK]", rut):
        raise ValidationError(MENSAJE_FORMATO_RUT)

    cuerpo, digito = rut.split("-")

    if digito != _digito_verificador(cuerpo):
        raise ValidationError(
            "El RUT no es válido: el dígito verificador no corresponde."
        )

    return rut