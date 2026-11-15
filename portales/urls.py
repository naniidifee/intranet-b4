from django.urls import path
from . import views

urlpatterns = [
    path(
        "estudiantes/horario/",
        views.horario_estudiante,
        name="horario_estudiante",
    ),
    path(
        "administrador/horarios/",
        views.gestionar_horarios,
        name="gestionar_horarios",
    ),
    path(
        "administrador/horarios/bloques/nuevo/",
        views.crear_bloque_horario,
        name="crear_bloque_horario",
    ),
    path(
        "administrador/horarios/clases/nueva/",
        views.crear_clase_horario,
        name="crear_clase_horario",
    ),
    path(
        "administrador/horarios/bloques/<int:bloque_id>/editar/",
        views.editar_bloque_horario,
        name="editar_bloque_horario",
    ),
    path(
        "administrador/horarios/bloques/<int:bloque_id>/eliminar/",
        views.eliminar_bloque_horario,
        name="eliminar_bloque_horario",
    ),
    path(
        "administrador/horarios/clases/<int:clase_id>/editar/",
        views.editar_clase_horario,
        name="editar_clase_horario",
    ),
    path(
        "administrador/horarios/clases/<int:clase_id>/eliminar/",
        views.eliminar_clase_horario,
        name="eliminar_clase_horario",
    ),
]