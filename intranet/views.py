from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .data import ESPECIALIDADES_DATA, equipo_data, NOTICIAS_DATA
from .models import Noticia


# -------------------------------------------------------------------
# Vistas Públicas e Intranet Base
# -------------------------------------------------------------------

def home(request):
    ultimas_noticias = Noticia.objects.all()[:3] 
    
    context = {
        'ultimas_noticias': ultimas_noticias,
    }
    return render(request, 'intranet/index.html', context)

def especialidad_detail(request, slug):
    # Busca la especialidad en el diccionario o lanza un error 404 si no existe
    esp = ESPECIALIDADES_DATA.get(slug)
    if not esp:
        raise Http404("Especialidad no encontrada")
    context = {
        'esp': esp
    }
    return render(request, 'intranet/especialidades.html', context)



def portal_noticias(request):
    # Obtener todas las noticias ordenadas de más reciente a más antigua
    noticias = Noticia.objects.all()
    
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
    noticia = get_object_or_404(Noticia, slug=slug)
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