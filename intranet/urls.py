from django.urls import path
from . import views

urlpatterns = [
    # Página pública principal (Inicio, Nosotros, Especialidades)
    path('', views.home, name='home'),
    
    # Módulo de Intranet
    path('intranet/', views.intranet_login, name='login'),

    path('intranet/dashboard/', views.intranet_dashboard, name='intranet_dashboard'),
    
    path('cerrar-sesion/', views.cerrar_sesion, name='logout'),

    # Ruta dinámica para las especialidades
    path('especialidades/<slug:slug>/', views.especialidad_detail, name='especialidad_detail'),

    # Ruta para las noticias
    path('noticias/', views.portal_noticias, name='portal_noticias'),
    path('noticias/<slug:slug>/', views.detalle_noticia, name='detalle_noticia'),

    # Ruta para el equipo de gestion
    path('equipo/', views.equipo_gestion, name='equipo_gestion'),

    # Ruta para proyecto educativo
    path('proyecto-educativo/', views.proyecto_educativo_view, name='proyecto_educativo'),

    # Ruta para egresados
    path('egresados/', views.egresados_view, name='egresados'),
    
    
    path('intranet/dashboard/', views.intranet_dashboard, name='intranet_dashboard'),


]
