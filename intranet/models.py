from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Comunicado(models.Model):
  titulo = models.CharField(max_length=200, verbose_name='Título')
  contenido = models.TextField(verbose_name='Contenido')
  fecha_creacion = models.DateTimeField(
      auto_now_add=True, verbose_name='Fecha de Creación'
  )
  autor = models.ForeignKey(
      User, on_delete=models.CASCADE, verbose_name='Autor'
  )

  class Meta:
    verbose_name = 'Comunicado'
    verbose_name_plural = 'Comunicados'
    ordering = ['-fecha_creacion']

  def __str__(self):
    return self.titulo