from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comunicado

# -------------------------------------------------------------------
# Vistas Públicas e Intranet Base
# -------------------------------------------------------------------

def home(request):
    return render(request, 'intranet/index.html')


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

    return render(request, 'intranet/login.html')


@login_required(login_url='login')
def intranet_dashboard(request):
    listado_comunicados = Comunicado.objects.all()[:5]
    return render(request, 'intranet/dashboard.html', {'comunicados': listado_comunicados})


@login_required(login_url='login')
def cerrar_sesion(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('login')


# -------------------------------------------------------------------
# CRUD de Comunicados (Con tu estructura estandarizada)
# -------------------------------------------------------------------

def comunicadoListView(request):
    return render(request, 'comunicado/comunicado_list.html', {'listado': Comunicado.objects.all()})


@login_required(login_url='login')
def comunicadoCreateView(request):
    # Asumiendo que usas un ComunicadoForm de forms.py
    form = ComunicadoForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            comunicado = form.save(commit=False)
            comunicado.autor = request.user
            comunicado.save()
            messages.success(request, 'Comunicado creado correctamente')
            return redirect('comunicado_list')
    return render(request, 'comunicado/comunicado_form.html', {'form': form})


@login_required(login_url='login')
def comunicadoUpdateView(request, id):
    comunicado = get_object_or_404(Comunicado, pk=id)
    form = ComunicadoForm(request.POST or None, request.FILES or None, instance=comunicado)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, 'Comunicado actualizado')
            return redirect('comunicado_list')
    return render(request, 'comunicado/comunicado_form.html', {'form': form})


def comunicadoDetailView(request, id):
    comunicado = get_object_or_404(Comunicado, pk=id)
    return render(request, 'comunicado/comunicado_detalle.html', {'c': comunicado})


@login_required(login_url='login')
def comunicadoDeleteView(request, id):
    comunicado = get_object_or_404(Comunicado, pk=id)
    if request.method == "POST":
        comunicado.delete()
        messages.success(request, 'Comunicado eliminado')
        return redirect('comunicado_list')
    return render(request, 'comunicado/comunicado_delete.html', {'c': comunicado})