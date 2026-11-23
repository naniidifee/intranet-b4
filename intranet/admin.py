from django.contrib import admin
from .models import NivelCurso, Taller

# Register your models here.

@admin.register(NivelCurso)
class NivelCursoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden")
    list_editable = ("orden",)


@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ("titulo", "activo", "orden")
    list_editable = ("activo", "orden")
    list_filter = ("activo", "niveles")
    search_fields = ("titulo", "descripcion")
    filter_horizontal = ("niveles",)