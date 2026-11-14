from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_View, name='logear'),    
    path('administrador/usuarios/nuevo/', views.crear_usuario, name="crear_usuario"),
]