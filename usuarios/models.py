from django.db import models
from django.contrib.auth.models import User

def rol_defecto():
    rol, _= Rol.objects.get_or_create(nombre="Estudiante")

class Rol(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre


class perfil(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.RESTRICT, default=rol_defecto)
    nombre_completo= models.CharField(max_length=25)
    rut = models.CharField(max_length=9)
    curso = models.CharField( max_length=25)

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
