from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_View, name='logear'),    
    path('administrador/usuarios/nuevo/', views.crear_usuario, name="crear_usuario"),
    path('administrador/usuarios/', views.listar_usuarios, name="listar_usuarios"),
    path('administrador/usuarios/<int:usuario_id>/editar/', views.editar_usuario, name="editar_usuario"),
    path('administrador/usuarios/<int:usuario_id>/estado/', views.cambiar_estado_usuario, name="cambiar_estado_usuario"),
]