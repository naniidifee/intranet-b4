from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .data import ESPECIALIDADES_DATA

from django.core.exceptions import PermissionDenied
from .forms import BloqueHorarioForm, ClaseHorarioForm
from .models import BloqueHorario, ClaseHorario, Comunicado
from django.views.decorators.http import require_POST
from datetime import date, datetime
from django.db.models import Q
import re


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

    return render(request, 'usuarios/login.html')


# Diccionario centralizado con la información de cada especialidad

def inicio(request):
    return render(request, 'intranet/index.html')

def especialidad_detail(request, slug):
    """Vista dinámica que carga los datos según la especialidad seleccionada."""
    esp = ESPECIALIDADES_DATA.get(slug)
    if not esp:
        return render(request, '404.html', status=404)
    return render(request, 'intranet/especialidades.html', {'esp': esp})

@login_required(login_url="login")
def horario_estudiante(request):
    try:
        perfil_estudiante = request.user.perfil
    except AttributeError:
        messages.error(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect("home")

    if perfil_estudiante.rol.nombre != "Estudiante":
        raise PermissionDenied

    curso = (perfil_estudiante.curso or "").strip()
    bloques = []

    if curso:
        clases_qs = (
            ClaseHorario.objects
            .filter(curso__iexact=curso)
            .select_related("bloque")
            .order_by("bloque__jornada", "bloque__orden", "dia", "grupo")
        )

        jornadas = list(
            clases_qs.values_list("bloque__jornada", flat=True).distinct()
        )
        clases = list(clases_qs)

        franjas = (
            BloqueHorario.objects
            .filter(
                Q(clases__curso__iexact=curso)
                | Q(tipo__in=["recreo", "almuerzo"], jornada__in=jornadas)
            )
            .distinct()
            .order_by("jornada", "orden", "hora_inicio")
        )

        for bloque in franjas:
            datos_bloque = {
                "tipo": bloque.tipo,
                "tipo_etiqueta": bloque.get_tipo_display(),
                "jornada": bloque.get_jornada_display(),
                "numero": bloque.numero,
                "hora_inicio": bloque.hora_inicio,
                "hora_fin": bloque.hora_fin,
            }

            if bloque.tipo == "clase":
                dias = []

                for numero_dia, nombre_dia in ClaseHorario.DIAS:
                    clases_dia = []

                    for clase in clases:
                        if clase.bloque_id != bloque.id or clase.dia != numero_dia:
                            continue

                        inicio = datetime.combine(date.today(), bloque.hora_inicio)
                        termino = datetime.combine(date.today(), bloque.hora_fin)
                        mitad = inicio + (termino - inicio) / 2

                        if clase.segmento == "primera_mitad":
                            hora_inicio, hora_fin = inicio.time(), mitad.time()
                        elif clase.segmento == "segunda_mitad":
                            hora_inicio, hora_fin = mitad.time(), termino.time()
                        else:
                            hora_inicio, hora_fin = inicio.time(), termino.time()

                        if clase.grupo != "todos":
                            modalidad_css = "partido-grupo"
                            grupo_etiqueta = clase.get_grupo_display()
                        elif clase.segmento != "completo":
                            modalidad_css = "partido-tiempo"
                            grupo_etiqueta = ""
                        else:
                            modalidad_css = "normal"
                            grupo_etiqueta = ""

                        clases_dia.append({
                            "tipo": clase.tipo,
                            "tipo_etiqueta": clase.get_tipo_display(),
                            "asignatura": clase.asignatura,
                            "hora_inicio": hora_inicio,
                            "hora_fin": hora_fin,
                            "docente": clase.docente,
                            "sala": clase.sala,
                            "modalidad_css": modalidad_css,
                            "grupo_etiqueta": grupo_etiqueta,
                            "segmento_etiqueta": (
                                clase.get_segmento_display()
                                if clase.segmento != "completo"
                                else ""
                            ),
                        })

                    dias.append({
                        "nombre": nombre_dia,
                        "clases": clases_dia,
                    })

                datos_bloque["dias"] = dias

            bloques.append(datos_bloque)

    return render(
        request,
        "intranet/estudiantes/horario.html",
        {"bloques": bloques},
    )

@login_required(login_url="login")
def intranet_dashboard(request):
    if request.user.is_superuser:
        return render(request, "usuarios/portal_administrador.html")
    try:
        rol = request.user.perfil.rol.nombre
    except AttributeError:
        messages.error(request, "Tu cuenta aún no tiene un rol asignado.")
        return redirect("home")

    if rol == "Administrador":
        return render(request, "usuarios/portal_administrador.html")

    if rol == "Estudiante":
        return redirect("horario_estudiante")

    messages.info(request, "La pantalla de tu rol aún está en preparación.")
    return redirect("home")

def _es_administrador(user):
    if user.is_superuser:
        return True

    try:
        return user.perfil.rol.nombre == "Administrador"
    except AttributeError:
        return False


def _verificar_administrador(request):
    if not _es_administrador(request.user):
        raise PermissionDenied

def _nivel_de_curso(nombre):
    coincidencia = re.match(r"\s*([1-4])\s*°", nombre)
    return coincidencia.group(1) if coincidencia else ""

@login_required(login_url="login")
def gestionar_horarios(request):
    _verificar_administrador(request)

    cursos = list(
        ClaseHorario.objects
        .order_by("curso")
        .values_list("curso", flat=True)
        .distinct()
    )

    niveles = [
        (numero, f"{numero}° Medio")
        for numero in ("1", "2", "3", "4")
        if any(_nivel_de_curso(curso) == numero for curso in cursos)
    ]

    nivel_solicitado = request.GET.get("nivel", "")
    niveles_validos = [valor for valor, _ in niveles]
    nivel_seleccionado = (
        nivel_solicitado
        if nivel_solicitado in niveles_validos
        else (niveles_validos[0] if niveles_validos else "")
    )

    cursos_nivel = [
        curso for curso in cursos
        if not nivel_seleccionado
        or _nivel_de_curso(curso) == nivel_seleccionado
    ]

    curso_solicitado = request.GET.get("curso", "").strip()
    curso_seleccionado = (
        curso_solicitado
        if curso_solicitado in cursos_nivel
        else (cursos_nivel[0] if cursos_nivel else "")
    )

    jornadas = BloqueHorario.JORNADAS
    jornada_seleccionada = request.GET.get("jornada", "manana")
    if jornada_seleccionada not in dict(jornadas):
        jornada_seleccionada = "manana"

    bloques = list(
        BloqueHorario.objects
        .filter(jornada=jornada_seleccionada)
        .order_by("orden", "hora_inicio")
    )

    clases = list(
        ClaseHorario.objects
        .filter(
            curso__iexact=curso_seleccionado,
            bloque__jornada=jornada_seleccionada,
        )
        .select_related("bloque")
        .order_by("dia", "grupo", "segmento")
    ) if curso_seleccionado else []

    matriz = []

    for bloque in bloques:
        fila = {
            "tipo": bloque.tipo,
            "tipo_etiqueta": bloque.get_tipo_display(),
            "numero": bloque.numero,
            "hora_inicio": bloque.hora_inicio,
            "hora_fin": bloque.hora_fin,
            "dias": [],
        }

        if bloque.tipo == "clase":
            for numero_dia, nombre_dia in ClaseHorario.DIAS:
                tarjetas = []

                for clase in clases:
                    if clase.bloque_id != bloque.id or clase.dia != numero_dia:
                        continue

                    inicio = datetime.combine(date.today(), bloque.hora_inicio)
                    termino = datetime.combine(date.today(), bloque.hora_fin)
                    mitad = inicio + (termino - inicio) / 2

                    if clase.segmento == "primera_mitad":
                        hora_inicio, hora_fin = inicio.time(), mitad.time()
                    elif clase.segmento == "segunda_mitad":
                        hora_inicio, hora_fin = mitad.time(), termino.time()
                    else:
                        hora_inicio, hora_fin = inicio.time(), termino.time()

                    modalidad = (
                        "partido-grupo" if clase.grupo != "todos"
                        else "partido-tiempo" if clase.segmento != "completo"
                        else "normal"
                    )

                    tarjetas.append({
                        "id": clase.id,
                        "asignatura": clase.asignatura,
                        "docente": clase.docente,
                        "sala": clase.sala,
                        "hora_inicio": hora_inicio,
                        "hora_fin": hora_fin,
                        "tipo_etiqueta": clase.get_tipo_display(),
                        "grupo_etiqueta": (
                            clase.get_grupo_display()
                            if clase.grupo != "todos"
                            else ""
                        ),
                        "segmento_etiqueta": (
                            clase.get_segmento_display()
                            if clase.segmento != "completo"
                            else ""
                        ),
                        "modalidad_css": modalidad,
                    })

                fila["dias"].append({
                    "nombre": nombre_dia,
                    "clases": tarjetas,
                })

        matriz.append(fila)

    return render(
        request,
        "intranet/horarios/gestionar.html",
        {
            "bloques": bloques,
            "clases": clases,
            "matriz": matriz,
            "cursos": cursos_nivel,
            "curso_seleccionado": curso_seleccionado,
            "jornadas": jornadas,
            "jornada_seleccionada": jornada_seleccionada,
            "niveles": niveles,
            "nivel_seleccionado": nivel_seleccionado,
        },
    )


@login_required(login_url="login")
def crear_bloque_horario(request):
    _verificar_administrador(request)
    form = BloqueHorarioForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "El bloque horario fue creado.")
        return redirect("gestionar_horarios")

    return render(
        request,
        "intranet/horarios/formulario.html",
        {"form": form, "titulo": "Crear bloque horario"},
    )


@login_required(login_url="login")
def crear_clase_horario(request):
    _verificar_administrador(request)
    form = ClaseHorarioForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La clase fue agregada al horario.")
        return redirect("gestionar_horarios")

    return render(
        request,
        "intranet/horarios/formulario.html",
        {"form": form, "titulo": "Agregar clase al horario"},
    )

@login_required(login_url="login")
def editar_bloque_horario(request, bloque_id):
    _verificar_administrador(request)
    bloque = get_object_or_404(BloqueHorario, pk=bloque_id)
    form = BloqueHorarioForm(request.POST or None, instance=bloque)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "El bloque horario fue actualizado.")
        return redirect("gestionar_horarios")

    return render(
        request,
        "intranet/horarios/formulario.html",
        {"form": form, "titulo": "Editar bloque horario"},
    )


@login_required(login_url="login")
@require_POST
def eliminar_bloque_horario(request, bloque_id):
    _verificar_administrador(request)
    bloque = get_object_or_404(BloqueHorario, pk=bloque_id)

    if bloque.clases.exists():
        messages.error(
            request,
            "No puedes eliminar este bloque porque tiene clases asignadas.",
        )
    else:
        bloque.delete()
        messages.success(request, "El bloque horario fue eliminado.")

    return redirect("gestionar_horarios")


@login_required(login_url="login")
def editar_clase_horario(request, clase_id):
    _verificar_administrador(request)
    clase = get_object_or_404(ClaseHorario, pk=clase_id)
    form = ClaseHorarioForm(request.POST or None, instance=clase)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La clase fue actualizada.")
        return redirect("gestionar_horarios")

    return render(
        request,
        "intranet/horarios/formulario.html",
        {"form": form, "titulo": "Editar clase"},
    )


@login_required(login_url="login")
@require_POST
def eliminar_clase_horario(request, clase_id):
    _verificar_administrador(request)
    clase = get_object_or_404(ClaseHorario, pk=clase_id)
    clase.delete()
    messages.success(request, "La clase fue eliminada del horario.")
    return redirect("gestionar_horarios")