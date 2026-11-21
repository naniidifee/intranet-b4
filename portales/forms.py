import os

from django import forms
from django.utils import timezone

from .cursos import CURSOS_CHOICES
from .models import BloqueHorario, ClaseHorario, HorarioArchivo, ReservaEspacio


class BloqueHorarioForm(forms.ModelForm):
    class Meta:
        model = BloqueHorario
        fields = [
            "tipo",
            "jornada",
            "numero",
            "orden",
            "hora_inicio",
            "hora_fin",
        ]
        labels = {
            "tipo": "Tipo de franja",
            "jornada": "Jornada",
            "numero": "Número de bloque (solo para clases)",
            "orden": "Orden en la jornada",
            "hora_inicio": "Hora de inicio",
            "hora_fin": "Hora de término",
        }
        widgets = {
            "hora_inicio": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time"},
            ),
            "hora_fin": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time"},
            ),
        }

    def clean(self):
        datos = super().clean()

        if (
            self.instance.pk
            and (self.instance.clases.exists() or self.instance.reservas.exists())
            and datos.get("tipo") != "clase"
        ):
            self.add_error(
                "tipo",
                "Este bloque tiene clases o reservas asignadas y no puede cambiarse a recreo o almuerzo.",
            )

        return datos


class ClaseHorarioForm(forms.ModelForm):
    class Meta:
        model = ClaseHorario
        fields = [
            "curso",
            "dia",
            "bloque",
            "asignatura",
            "docente",
            "sala",
            "tipo",
            "grupo",
            "segmento",
        ]
        labels = {
            "curso": "Curso",
            "dia": "Día",
            "bloque": "Bloque de clase",
            "asignatura": "Asignatura",
            "docente": "Profesor/a",
            "sala": "Sala",
            "tipo": "Tipo de asignatura",
            "grupo": "Grupo",
            "segmento": "Parte del bloque",
        }
        widgets = {
            "curso": forms.TextInput(attrs={"placeholder": "Ejemplo: 1° Medio A"}),
            "asignatura": forms.TextInput(attrs={"placeholder": "Asignatura"}),
            "docente": forms.TextInput(attrs={"placeholder": "Nombre del docente"}),
            "sala": forms.TextInput(attrs={"placeholder": "Ejemplo: Sala 1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bloque"].queryset = BloqueHorario.objects.filter(tipo="clase")

    def clean_curso(self):
        return self.cleaned_data["curso"].strip()

class HorarioArchivoForm(forms.Form):
    """Sube el horario de un curso como PDF o imagen (PNG/JPG)."""

    FIRMAS = {
        ".pdf": (b"%PDF-",),
        ".png": (b"\x89PNG\r\n\x1a\n",),
        ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",),
    }
    TAMANO_MAXIMO = 10 * 1024 * 1024  # 10 MB

    curso = forms.ChoiceField(choices=CURSOS_CHOICES, label="Curso")
    archivo = forms.FileField(
        label="Archivo del horario (PDF o PNG)",
        widget=forms.ClearableFileInput(
            attrs={"accept": ".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"}
        ),
    )

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        extension = os.path.splitext(archivo.name)[1].lower()

        if extension not in self.FIRMAS:
            raise forms.ValidationError("El archivo debe ser PDF o imagen PNG/JPG.")

        if archivo.size > self.TAMANO_MAXIMO:
            raise forms.ValidationError("El archivo no puede superar los 10 MB.")

        encabezado = archivo.read(8)
        archivo.seek(0)

        if not any(encabezado.startswith(firma) for firma in self.FIRMAS[extension]):
            raise forms.ValidationError(
                "El contenido no coincide con el formato del archivo."
            )

        return archivo

    def guardar(self, usuario):
        """Crea o reemplaza el horario del curso y borra el archivo anterior."""
        curso = self.cleaned_data["curso"]
        archivo = self.cleaned_data["archivo"]

        horario, _ = HorarioArchivo.objects.get_or_create(curso=curso)
        anterior = horario.archivo.name if horario.archivo else ""

        horario.archivo = archivo
        horario.subido_por = usuario
        horario.save()

        if anterior and anterior != horario.archivo.name:
            horario.archivo.storage.delete(anterior)

        return horario


class SolicitudReservaForm(forms.Form):
    """Datos que envía un docente para pedir un espacio."""

    espacio = forms.ChoiceField(choices=ReservaEspacio.ESPACIOS)
    fecha = forms.DateField(input_formats=["%Y-%m-%d"])
    bloque = forms.ModelChoiceField(
        queryset=BloqueHorario.objects.filter(tipo="clase"),
    )
    motivo = forms.CharField(
        max_length=150,
        error_messages={"required": "Indica el motivo o el curso de la reserva."},
    )

    def __init__(self, *args, docente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.docente = docente

    def clean(self):
        datos = super().clean()
        espacio = datos.get("espacio")
        fecha = datos.get("fecha")
        bloque = datos.get("bloque")

        if not (espacio and fecha and bloque):
            return datos

        ahora = timezone.localtime()

        if fecha.weekday() > 4:
            raise forms.ValidationError("Solo se puede reservar de lunes a viernes.")

        if fecha < ahora.date() or (
            fecha == ahora.date() and bloque.hora_fin <= ahora.time()
        ):
            raise forms.ValidationError("No puedes reservar un bloque que ya pasó.")

        if ReservaEspacio.objects.filter(
            espacio=espacio, fecha=fecha, bloque=bloque, estado="aprobada",
        ).exists():
            raise forms.ValidationError(
                "Ese bloque ya está reservado por otro docente."
            )

        if self.docente and ReservaEspacio.objects.filter(
            docente=self.docente,
            espacio=espacio,
            fecha=fecha,
            bloque=bloque,
            estado__in=["pendiente", "aprobada"],
        ).exists():
            raise forms.ValidationError("Ya tienes una solicitud para ese bloque.")

        return datos
