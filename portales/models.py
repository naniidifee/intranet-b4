from django.db import models
from django.contrib.auth.models import User
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

class ReservaEspacio(models.Model):
    ESPACIOS = [
        ("biblioteca", "Biblioteca"),
        ("laboratorio", "Laboratorio"),
        ("gimnasio", "Gimnasio"),
        ("patio_central", "Patio central"),
        ("cancha", "Cancha"),
    ]

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]

    docente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reservas_espacios",
    )
    espacio = models.CharField(max_length=30, choices=ESPACIOS)
    fecha = models.DateField()
    bloque = models.ForeignKey(
        BloqueHorario,
        on_delete=models.PROTECT,
        related_name="reservas_espacios",
    )
    motivo = models.TextField()
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default="pendiente",
    )
    respuesta_administracion = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_solicitud"]

    def __str__(self):
        return f"{self.get_espacio_display()} - {self.fecha} - {self.get_estado_display()}"