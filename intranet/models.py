from django.db import models
from django.utils import timezone

# Create your models here.
class Noticia(models.Model):
    CATEGORIAS = [
        ('Académico', 'Académico'),
        ('Institucional', 'Institucional'),
        ('Actividades', 'Actividades'),
        ('Comunidad', 'Comunidad'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, max_length=200)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='Institucional')
    descripcion = models.TextField(verbose_name="Bajada / Resumen corto")
    contenido = models.TextField(verbose_name="Contenido completo")
    imagen = models.ImageField(upload_to='noticias/', blank=True, null=True, verbose_name="Imagen Principal")
    autor = models.CharField(max_length=100, default="Comunicaciones AVB")
    fecha = models.DateField(default=timezone.now, verbose_name="Fecha de publicación")
    destacado = models.BooleanField(default=False, verbose_name="Marcar como destacado")

    class Meta:
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo