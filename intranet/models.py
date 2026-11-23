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
    
    publicada = models.BooleanField(
        default=True,
        verbose_name="Publicada",
    )

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

# models de talleres
class NivelCurso(models.Model):
    nombre = models.CharField(max_length=40, unique=True)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Nivel / Curso"
        verbose_name_plural = "Niveles / Cursos"

    def __str__(self):
        return self.nombre


class Taller(models.Model):
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to="talleres/")
    niveles = models.ManyToManyField(NivelCurso, related_name="talleres", blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["orden", "titulo"]
        verbose_name = "Taller"
        verbose_name_plural = "Talleres"

    def __str__(self):
        return self.titulo