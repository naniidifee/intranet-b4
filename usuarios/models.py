from django.db import models
from django.contrib.auth.models import User

def rol_defecto():
    rol, _ = Rol.objects.get_or_create(nombre="Estudiante")
    return rol.pk

class Rol(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre


class perfil(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.RESTRICT, default=rol_defecto)
    nombre_completo= models.CharField(max_length=25)
    rut = models.CharField(max_length=10)
    curso = models.CharField( max_length=25)

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

class SolicitudRecuperacion(models.Model):

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]

    rut = models.CharField(max_length=10)
    nombre_completo = models.CharField(max_length=100)
    curso = models.CharField(max_length=25, blank=True)
    correo = models.EmailField(max_length=254)
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default="pendiente",
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_solicitud"]
        verbose_name = "solicitud de recuperación"
        verbose_name_plural = "solicitudes de recuperación"

    def __str__(self):
        return f"{self.rut} - {self.estado}"