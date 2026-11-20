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

ESPACIOS = [("", "Selecciona una sala o espacio")]

for numero in range(1, 41):
    nombre = f"Sala {numero:02}"
    ESPACIOS.append((nombre, nombre))

ESPACIOS += [
    ("Biblioteca", "Biblioteca"),
    ("Laboratorio", "Laboratorio"),
    ("Gimnasio", "Gimnasio"),
    ("Cancha", "Cancha"),
    ("Patio central", "Patio central"),
]


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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["bloque"].queryset = BloqueHorario.objects.filter(
            tipo="clase"
        )

        opciones_sala = ESPACIOS.copy()
        sala_actual = self.instance.sala

        if sala_actual and sala_actual not in dict(opciones_sala):
            opciones_sala.insert(
                1,
                (sala_actual, f"{sala_actual} (nombre actual)"),
            )

        self.fields["sala"] = forms.ChoiceField(
            choices=opciones_sala,
            required=False,
            label="Sala o espacio",
        )

    def clean_curso(self):
        return self.cleaned_data["curso"].strip()

class ImportarHorarioPDFForm(forms.Form):
    archivo = forms.FileField(label="Selecciona el horario en PDF")

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]

        if not archivo.name.lower().endswith(".pdf"):
            raise forms.ValidationError("El archivo debe tener formato PDF.")

        if archivo.size > 20 * 1024 * 1024:
            raise forms.ValidationError("El PDF no puede superar los 20 MB.")

        encabezado = archivo.read(5)
        archivo.seek(0)

        if encabezado != b"%PDF-":
            raise forms.ValidationError("El archivo seleccionado no parece ser un PDF válido.")

        return archivo