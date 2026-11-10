from django.urls import path
from . import views

urlpatterns = [
    # Página pública principal (Inicio, Nosotros, Especialidades)
    path('', views.home, name='home'),
    
    # Módulo de Intranet
    path('intranet/', views.intranet_login, name='login'),
    path('intranet/panel/', views.intranet_dashboard, name='intranet_dashboard'),
    path('intranet/salir/', views.cerrar_sesion, name='logout'),
]