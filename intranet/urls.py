from django.urls import path
from . import views

urlpatterns = [
    # Página pública principal (Inicio, Nosotros, Especialidades)
    path('', views.home, name='home'),
    
    # Módulo de Intranet
    path('intranet/', views.intranet_login, name='login'),

     # Ruta dinámica para las especialidades
    path('especialidades/<slug:slug>/', views.especialidad_detail, name='especialidad_detail'),
    
]