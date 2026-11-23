from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .data import ESPECIALIDADES_DATA, equipo_data
from .models import Noticia, Taller


# -------------------------------------------------------------------
# Vistas Públicas e Intranet Base
# -------------------------------------------------------------------

def home(request):

    ultimas_noticias = Noticia.objects.filter(publicada=True)[:3]
    
    context = {
        'ultimas_noticias': ultimas_noticias,
    }
    return render(request, 'intranet/index.html', context)



def intranet_login(request):
    if request.method == "POST":
        usuario = request.POST.get('username')
        contrasena = request.POST.get('password')
        user = authenticate(request, username=usuario, password=contrasena)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido/a {user.username}')
            return redirect('intranet_dashboard')
        else:
            messages.error(request, 'Credenciales incorrectas. Verifique su usuario y contraseña.')

    return render(request, 'usuarios/login.html')

def cerrar_sesion(request):
    logout(request)
    return redirect("login")


# Diccionario centralizado con la información de cada especialidad

def inicio(request):
    return render(request, 'intranet/index.html')

def especialidad_detail(request, slug):
    # Busca la especialidad en el diccionario o lanza un error 404 si no existe
    esp = ESPECIALIDADES_DATA.get(slug)
    if not esp:
        raise Http404("Especialidad no encontrada")
    context = {
        'esp': esp
    }
    return render(request, 'intranet/especialidades.html', context)


@login_required(login_url="login")
def intranet_dashboard(request):
    if request.user.is_superuser:
        return render(request, "portales/portal_administrador.html")
    try:
        rol = request.user.perfil.rol.nombre
    except AttributeError:
        messages.error(request, "Tu cuenta aún no tiene un rol asignado.")
        return redirect("home")

    if rol == "Administrador":
        return render(request, "portales/portal_administrador.html")

    if rol == "Estudiante":
        return redirect("horario_estudiante")
    
    if rol == "Docente":
        return redirect("reservar_espacios")

    messages.info(request, "La pantalla de tu rol aún está en preparación.")
    return redirect("home")


def portal_noticias(request):
    # Obtener todas las noticias ordenadas de más reciente a más antigua
    noticias = Noticia.objects.filter(publicada=True)
    
    # Filtro opcional por categoría si viene en la URL (?categoria=Académico)
    categoria_query = request.GET.get('categoria')
    if categoria_query and categoria_query != 'todas':
        noticias = noticias.filter(categoria=categoria_query)
        
    context = {
        'noticias': noticias,
        'categoria_activa': categoria_query or 'todas'
    }
    return render(request, 'intranet/noticias.html', context)

def detalle_noticia(request, slug):
    noticia = get_object_or_404(
        Noticia,
        slug=slug,
        publicada=True,
    )
    context = {
        'noticia': noticia
    }
    return render(request, 'intranet/detalle_noticia.html', context)

def equipo_gestion(request):
    return render(request, 'intranet/equipo.html', {'equipo': equipo_data})


def proyecto_educativo_view(request):
    return render(request, 'intranet/proyecto_educativo.html') 

def egresados_view(request):
    return render(request, 'intranet/egresados.html')

def valores_view(request):
    return render(request, 'intranet/valores.html')

def talleres_view(request):
    talleres = Taller.objects.filter(activo=True).prefetch_related("niveles")
    return render(request, "intranet/talleres.html", {"taller": talleres})
