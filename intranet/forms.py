from django import forms

from .models import BloqueHorario, ClaseHorario


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
            and self.instance.clases.exists()
            and datos.get("tipo") != "clase"
        ):
            self.add_error(
                "tipo",
                "Este bloque tiene clases asignadas y no puede cambiarse a recreo o almuerzo.",
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