from django.urls import path
from . import views

urlpatterns = [
    # Página pública principal (Inicio, Nosotros, Especialidades)
    path('', views.home, name='home'),
    
    # Ruta dinámica para las especialidades
    path('especialidades/<slug:slug>/', views.especialidad_detail, name='especialidad_detail'),

    # Ruta para las noticias
    path('noticias/', views.portal_noticias, name='portal_noticias'),
    path('noticias/<str:noticia_id>/', views.detalle_noticia, name='detalle_noticia'),

    # Ruta para el equipo de gestion
    path('equipo/', views.equipo_gestion, name='equipo_gestion'),

    # Ruta para proyecto educativo
    path('proyecto-educativo/', views.proyecto_educativo_view, name='proyecto_educativo'),

    # Ruta para egresados
    path('egresados/', views.egresados_view, name='egresados'),

]
