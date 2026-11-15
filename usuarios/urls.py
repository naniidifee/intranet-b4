from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy



urlpatterns = [
    path('login/', views.login_View, name='logear'),    
    path('administrador/usuarios/nuevo/', views.crear_usuario, name="crear_usuario"),
    path('administrador/usuarios/', views.listar_usuarios, name="listar_usuarios"),
    path('administrador/usuarios/<int:usuario_id>/editar/', views.editar_usuario, name="editar_usuario"),
    path('administrador/usuarios/<int:usuario_id>/estado/', views.cambiar_estado_usuario, name="cambiar_estado_usuario"),
    path('recuperar-contrasena/', views.solicitar_recuperacion, name="solicitar_recuperacion"),
    path('administrador/solicitudes-recuperacion/', views.listar_solicitudes_recuperacion, name="listar_solicitudes_recuperacion"),
    path('administrador/solicitudes-recuperacion/<int:solicitud_id>/resolver/', views.resolver_solicitud_recuperacion, name="resolver_solicitud_recuperacion"),
    path(
        "recuperar-contrasena/confirmar/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="usuarios/restablecer_contrasena.html",
            success_url=reverse_lazy("login"),
        ),
        name="password_reset_confirm",
    ),

]