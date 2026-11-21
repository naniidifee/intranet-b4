from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError

from portales.cursos import CURSOS_CHOICES
from .models import Rol, perfil, SolicitudRecuperacion
from .validators import MENSAJE_FORMATO_RUT, PATRON_RUT_HTML, validar_rut


ROLES = [
    ("Administrador", "Administrador"),
    ("Estudiante", "Estudiante"),
    ("Docente", "Docente"),
    ("Inspectoría", "Inspectoría"),
]


class CrearUsuarioForm(UserCreationForm):
    nombre_completo = forms.CharField(
        max_length=25,
        label="Nombre completo",
    )
    rol = forms.ChoiceField(
        choices=ROLES,
        label="Rol",
    )
    curso = forms.ChoiceField(
        choices=CURSOS_CHOICES,
        required=False,
        label="Curso",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "nombre_completo", "rol", "curso")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "RUT (será el usuario de acceso)"
        self.fields["username"].help_text = (
            "Ingresa el RUT sin puntos y con guion. Ejemplo: 12345678-5."
        )
        self.fields["username"].widget.attrs.update({
            "maxlength": "10",
            "placeholder": "12345678-5",
            "pattern": PATRON_RUT_HTML,
            "title": MENSAJE_FORMATO_RUT,
            "autocomplete": "off",
        })

    def clean_username(self):
        # Valida el formato y el dígito verificador antes de revisar si ya existe.
        self.cleaned_data["username"] = validar_rut(
            self.cleaned_data.get("username")
        )
        return super().clean_username()
    
    def clean(self):
        datos = super().clean()

        if (
            datos.get("rol") == "Estudiante"
            and not datos.get("curso", "").strip()
        ):
            self.add_error("curso", "Indica el curso del estudiante.")

        return datos

    @transaction.atomic
    def save(self, commit=True):
        usuario = super().save(commit=False)
        rol_nombre = self.cleaned_data["rol"]
        usuario.is_staff = rol_nombre == "Administrador"

        if commit:
            usuario.save()

            rol, _ = Rol.objects.get_or_create(nombre=rol_nombre)

            perfil.objects.create(
                usuario=usuario,
                nombre_completo=self.cleaned_data["nombre_completo"],
                rut=usuario.username,
                curso=(
                    self.cleaned_data.get("curso", "").strip()
                    if rol_nombre == "Estudiante"
                    else ""
                ),
                rol=rol,
            )

        return usuario

class SolicitudRecuperacionForm(forms.ModelForm):
    class Meta:
        model = SolicitudRecuperacion
        fields = (
            "rut",
            "nombre_completo",
            "curso",
            "correo",
        )
        labels = {
            "rut": "RUT",
            "nombre_completo": "Nombre completo",
            "curso": "Curso (si corresponde)",
            "correo": "Correo para recibir instrucciones",
        }
        widgets = {
            "rut": forms.TextInput(attrs={
                "placeholder": "12345678-5",
                "maxlength": "10",
                "pattern": PATRON_RUT_HTML,
                "title": MENSAJE_FORMATO_RUT,
                "autocomplete": "off",
            }),
            "nombre_completo": forms.TextInput(attrs={
                "placeholder": "Nombre y apellidos",
            }),
            "curso": forms.TextInput(attrs={
                "placeholder": "Por ejemplo: 4°A",
            }),
            "correo": forms.EmailInput(attrs={
                "placeholder": "nombre@correo.com",
            }),
        }

    def clean_rut(self):
        return validar_rut(self.cleaned_data["rut"])

    def clean_nombre_completo(self):
        return self.cleaned_data["nombre_completo"].strip()

    def clean_curso(self):
        return self.cleaned_data["curso"].strip()

class EditarPerfilUsuarioForm(forms.ModelForm):
    curso = forms.CharField(
        max_length=25,
        required=False,
        label="Curso",
    )

    class Meta:
        model = perfil
        fields = ("nombre_completo", "rol", "curso")
        labels = {
            "nombre_completo": "Nombre completo",
            "rol": "Rol",
        }