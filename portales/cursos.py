"""Catálogo de cursos del liceo, para usarlo en listas desplegables."""

import re

ESPECIALIDADES_TP = {
    "A": "Administración",
    "B": "Turismo",
    "C": "Electricidad",
    "D": "Gastronomía",
    "E": "Electrónica",
    "F": "Programación",
    "G": "Administración",
    "H": "Turismo",
    "I": "Electricidad",
    "J": "Gastronomía",
}

NIVELES = [
    ("1", "1° Medio"),
    ("2", "2° Medio"),
    ("3", "3° Medio"),
    ("4", "4° Medio"),
]

CURSOS_CATALOGO = [
    "1A 410", "1B 410", "1C 410",
    "1A 510", "1B 510", "1C 510", "1D 510",
    "1A 610", "1B 610", "1C 610",

    "2A 410", "2B 410", "2C 410",
    "2A 510", "2B 510", "2C 510", "2D 510",
    "2A 610", "2B 610", "2C 610",

    "3A 410", "3B 410",
    "3A 510", "3B 510", "3C 510", "3D 510", "3E 510",
    "3A 610", "3B 610", "3C 610",

    "4A 410", "4B 410",
    "4A 510", "4B 510", "4C 510", "4D 510", "4E 510",
    "4A 610", "4B 610", "4C 610",
]


def etiqueta_curso(codigo):
    """Convierte '3B 510' en 'B — Turismo (510)'."""
    coincidencia = re.match(
        r"^\s*([1-4])\s*([A-J])\s*(.*)$",
        codigo,
        re.IGNORECASE,
    )

    if not coincidencia:
        return codigo

    nivel, paralelo, identificador = coincidencia.groups()
    paralelo = paralelo.upper()

    if nivel in {"1", "2"}:
        especialidad = "Formación General"
    else:
        especialidad = ESPECIALIDADES_TP.get(paralelo, "Especialidad técnica")

    etiqueta = f"{paralelo} — {especialidad}"

    if identificador.strip():
        etiqueta += f" ({identificador.strip()})"

    return etiqueta


def _construir_opciones():
    """Opciones agrupadas por nivel: el valor guardado es el código ('3B 510')."""
    grupos = []
    for nivel, nombre_nivel in NIVELES:
        opciones = [
            (codigo, f"{nombre_nivel} {etiqueta_curso(codigo)}")
            for codigo in CURSOS_CATALOGO
            if codigo.startswith(nivel)
        ]
        grupos.append((nombre_nivel, opciones))
    return grupos


# Lista lista para usar en un campo de formulario (con opción vacía al inicio)
CURSOS_CHOICES = [("", "Selecciona un curso")] + _construir_opciones()
