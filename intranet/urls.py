from django.urls import path
from . import views

urlpatterns = [
    # Página pública principal (Inicio, Nosotros, Especialidades)
    path('', views.home, name='home'),
    
    # Módulo de Intranet
    path('intranet/', views.intranet_login, name='login'),

    # Ruta dinámica para las especialidades
    path('especialidades/<slug:slug>/', views.especialidad_detail, name='especialidad_detail'),

    path('estudiantes/horario/', views.horario_estudiante, name='horario_estudiante'),

    path('intranet/dashboard/', views.intranet_dashboard, name='intranet_dashboard'),
    path('administrador/horarios/', views.gestionar_horarios, name="gestionar_horarios"),
    path("administrador/horarios/bloques/nuevo/", views.crear_bloque_horario, name="crear_bloque_horario"),
    path("administrador/horarios/clases/nueva/", views.crear_clase_horario, name="crear_clase_horario"),
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