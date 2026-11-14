from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Rol, perfil


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
    curso = forms.CharField(
        max_length=25,
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
            "Ingresa el RUT sin puntos y con guion. Ejemplo: 12345678-K."
        )
        self.fields["username"].widget.attrs.update({
            "maxlength": "10",
            "placeholder": "12345678-K",
        })
    def clean_username(self):
        username = super().clean_username()

        if len(username) > 10:
            raise ValidationError("El RUT no debe superar los 10 caracteres.")

        return username
    
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
                curso=self.cleaned_data.get("curso", "").strip(),
                rol=rol,
            )

        return usuario