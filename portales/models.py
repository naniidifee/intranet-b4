import os
import re
import uuid

from django.conf import settings
from django.db import models

# Create your models here.

class BloqueHorario(models.Model):
    TIPOS = [
        ("clase", "Bloque de clases"),
        ("recreo", "Recreo"),
        ("almuerzo", "Almuerzo"),
    ]

    JORNADAS = [
        ("manana", "Mañana"),
        ("tarde", "Tarde"),
    ]

    numero = models.PositiveSmallIntegerField(
        unique=True,
        null=True,
        blank=True,
    )
    orden = models.PositiveSmallIntegerField(default=1)
    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
        default="clase",
    )
    jornada = models.CharField(
        max_length=10,
        choices=JORNADAS,
        default="manana",
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        ordering = ["jornada", "orden", "hora_inicio"]
        verbose_name = "bloque horario"
        verbose_name_plural = "bloques horarios"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            raise ValidationError(
                "La hora de término debe ser posterior a la de inicio."
            )

        if self.tipo == "clase" and not self.numero:
            raise ValidationError("Los bloques de clase deben tener un número.")

    def __str__(self):
        if self.numero:
            etiqueta = f"Bloque {self.numero}"
        else:
            etiqueta = self.get_tipo_display()

        return (
            f"{etiqueta} "
            f"({self.hora_inicio:%H:%M}–{self.hora_fin:%H:%M})"
        )


class ClaseHorario(models.Model):
    DIAS = [
        (1, "Lunes"),
        (2, "Martes"),
        (3, "Miércoles"),
        (4, "Jueves"),
        (5, "Viernes"),
    ]

    TIPOS = [
        ("normal", "Clase normal"),
        ("electiva", "Electiva"),
        ("especialidad", "Especialidad"),
        ("taller", "Taller"),
    ]

    GRUPOS = [
        ("todos", "Curso completo"),
        ("A", "Grupo A"),
        ("B", "Grupo B"),
    ]

    SEGMENTOS = [
        ("completo", "Bloque completo"),
        ("primera_mitad", "Primera mitad"),
        ("segunda_mitad", "Segunda mitad"),
    ]

    curso = models.CharField(max_length=25)
    dia = models.PositiveSmallIntegerField(choices=DIAS)
    bloque = models.ForeignKey(
        BloqueHorario,
        on_delete=models.PROTECT,
        related_name="clases",
    )
    asignatura = models.CharField(max_length=100)
    docente = models.CharField(max_length=100)
    sala = models.CharField(max_length=50, blank=True)
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default="normal",
    )
    grupo = models.CharField(
        max_length=10,
        choices=GRUPOS,
        default="todos",
    )
    segmento = models.CharField(
        max_length=20,
        choices=SEGMENTOS,
        default="completo",
    )

    class Meta:
        ordering = [
            "curso",
            "dia",
            "bloque__jornada",
            "bloque__orden",
            "segmento",
            "grupo",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["curso", "dia", "bloque", "grupo", "segmento"],
                name='horario_unico_por_grupo_y_segmento_portales',
            ),
        ]
        verbose_name = "clase de horario"
        verbose_name_plural = "clases de horario"

    def __str__(self):
        return f"{self.curso} - {self.get_dia_display()} - {self.asignatura}"


def ruta_horario(instance, filename):
    """Guarda el archivo como horarios/<curso>-<id aleatorio>.<ext>."""
    extension = os.path.splitext(filename)[1].lower()
    curso = re.sub(r"[^A-Za-z0-9]+", "-", instance.curso).strip("-") or "curso"
    return f"horarios/{curso}-{uuid.uuid4().hex[:8]}{extension}"


class HorarioArchivo(models.Model):
    """Horario de un curso subido como PDF o imagen (uno por curso)."""

    curso = models.CharField(max_length=25, unique=True)
    archivo = models.FileField(upload_to=ruta_horario)
    actualizado = models.DateTimeField(auto_now=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        ordering = ["curso"]
        verbose_name = "horario en archivo"
        verbose_name_plural = "horarios en archivo"

    def __str__(self):
        return f"Horario {self.curso}"

    @property
    def extension(self):
        return os.path.splitext(self.archivo.name)[1].lower()

    @property
    def es_pdf(self):
        return self.extension == ".pdf"

    @property
    def es_imagen(self):
        return self.extension in {".png", ".jpg", ".jpeg"}

    @property
    def nombre_descarga(self):
        curso = re.sub(r"[^A-Za-z0-9]+", "-", self.curso).strip("-") or "curso"
        return f"horario-{curso}{self.extension}"

    def delete(self, *args, **kwargs):
        nombre = self.archivo.name
        almacenamiento = self.archivo.storage
        resultado = super().delete(*args, **kwargs)
        if nombre:
            almacenamiento.delete(nombre)
        return resultado
