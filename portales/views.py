import mimetypes
import re
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.text import capfirst, slugify
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from intranet.models import Noticia, Taller

from .forms import BloqueHorarioForm, ClaseHorarioForm, HorarioArchivoForm, NoticiaForm, SolicitudReservaForm
from .models import BloqueHorario, ClaseHorario, HorarioArchivo, ReservaEspacio

from correo_avb.recuperacion import procesar_recuperacion_usuario
from .models import SolicitudRecuperacion

# Create your views here.

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
    electividades = []
    talleres = []

    archivo_horario = (
        HorarioArchivo.objects.filter(curso__iexact=curso).first()
        if curso else None
    )

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

        for clase in clases:
            if clase.tipo == "electiva":
                electividades.append(clase)

            if clase.tipo == "taller":
                talleres.append(clase)

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

    Usuario = get_user_model()

    companeros = (
        Usuario.objects
        .filter(perfil__curso__iexact=curso, perfil__rol__nombre="Estudiante")
        .select_related("perfil")
        .order_by("perfil__nombre_completo")
    )

    return render(
        request,
        "portales/estudiantes/horario.html",
        {
            "bloques": bloques,
            "electividades": electividades,
            "talleres": talleres,
            "companeros": companeros,
            "archivo_horario": archivo_horario,
        },
    )

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

def _verificar_docente(request):
    try:
        es_docente = request.user.perfil.rol.nombre == "Docente"
    except AttributeError:
        es_docente = False

    if not es_docente:
        raise PermissionDenied


@login_required(login_url="login")
def reservar_espacios(request):
    _verificar_docente(request)

    ahora = timezone.localtime()
    hoy = ahora.date()
    espacios = ReservaEspacio.ESPACIOS

    espacio = request.GET.get("espacio", "")
    if espacio not in dict(espacios):
        espacio = espacios[0][0]

    semana = _parsear_fecha(request.GET.get("semana"))
    if semana is None:
        semana = hoy + timedelta(days=7 - hoy.weekday()) if hoy.weekday() > 4 else hoy
    lunes = semana - timedelta(days=semana.weekday())
    dias = [lunes + timedelta(days=i) for i in range(5)]

    reservas = (
        ReservaEspacio.objects
        .filter(
            espacio=espacio,
            fecha__range=(dias[0], dias[-1]),
            estado__in=["pendiente", "aprobada"],
        )
        .select_related("docente__perfil")
    )

    aprobadas = {}
    propias = {}
    for reserva in reservas:
        clave = (reserva.fecha, reserva.bloque_id)
        if reserva.estado == "aprobada":
            aprobadas[clave] = reserva
        if reserva.docente_id == request.user.id:
            propias[clave] = reserva

    filas = []
    for bloque in BloqueHorario.objects.all():
        fila = {
            "id": bloque.id,
            "es_clase": bloque.tipo == "clase",
            "etiqueta": bloque.get_tipo_display(),
            "inicio": bloque.hora_inicio,
            "fin": bloque.hora_fin,
            "celdas": [],
        }

        if fila["es_clase"]:
            for dia in dias:
                clave = (dia, bloque.id)
                celda = {
                    "fecha": dia,
                    "resumen": capfirst(date_format(dia, r"l j \d\e F")),
                }
                propia = propias.get(clave)
                ocupada = aprobadas.get(clave)

                if dia < hoy or (dia == hoy and bloque.hora_fin <= ahora.time()):
                    celda["estado"] = "pasado"
                elif propia is not None:
                    celda["estado"] = "mia" if propia.estado == "aprobada" else "pendiente"
                    celda["reserva_id"] = propia.id
                    celda["motivo"] = propia.motivo
                elif ocupada is not None:
                    celda["estado"] = "ocupado"
                    celda["docente"] = _nombre_docente(ocupada.docente)
                else:
                    celda["estado"] = "disponible"

                fila["celdas"].append(celda)

        filas.append(fila)

    mis_solicitudes = (
        ReservaEspacio.objects
        .filter(docente=request.user)
        .select_related("bloque")[:15]
    )

    return render(
        request,
        "portales/docente/reservar_espacios.html",
        {
            "espacios": espacios,
            "espacio": espacio,
            "espacio_nombre": dict(espacios)[espacio],
            "dias": dias,
            "lunes": dias[0],
            "viernes": dias[-1],
            "semana_numero": dias[0].isocalendar()[1],
            "anterior": dias[0] - timedelta(days=7),
            "siguiente": dias[0] + timedelta(days=7),
            "filas": filas,
            "mis_solicitudes": mis_solicitudes,
        },
    )


@login_required(login_url="login")
def lista_curso_docente(request):
    _verificar_docente(request)

    perfil = request.user.perfil
    nombre_docente = perfil.nombre_completo or request.user.username

    # ClaseHorario.docente es texto; buscamos el nombre del usuario
    # entre las asignaciones registradas en los horarios.
    clases_docente = ClaseHorario.objects.filter(
        docente__icontains=nombre_docente
    )

    cursos = list(
        clases_docente
        .exclude(curso="")
        .values_list("curso", flat=True)
        .distinct()
        .order_by("curso")
    )

    curso_seleccionado = request.GET.get("curso", "")
    if curso_seleccionado not in cursos:
        curso_seleccionado = cursos[0] if cursos else ""

    Usuario = get_user_model()

    if curso_seleccionado:
        estudiantes = (
            Usuario.objects
            .filter(
                perfil__rol__nombre="Estudiante",
                perfil__curso__iexact=curso_seleccionado,
            )
            .select_related("perfil")
            .order_by("perfil__nombre_completo")
        )

        asignaturas = (
            clases_docente
            .filter(curso__iexact=curso_seleccionado)
            .values_list("asignatura", flat=True)
            .distinct()
            .order_by("asignatura")
        )

        coincidencia = re.match(
            r"^\s*[1-4]\s*(?:°?\s*medio\s*)?([A-J])",
            curso_seleccionado,
            re.IGNORECASE,
        )
        especialidad = (
            ESPECIALIDADES_TP.get(coincidencia.group(1).upper(), "Formación General")
            if coincidencia
            else "Formación General"
        )
    else:
        estudiantes = Usuario.objects.none()
        asignaturas = []
        especialidad = ""

    return render(
        request,
        "portales/docente/lista_curso.html",
        {
            "cursos": cursos,
            "curso_seleccionado": curso_seleccionado,
            "estudiantes": estudiantes,
            "total_alumnos": estudiantes.count(),
            "asignaturas": asignaturas,
            "especialidad": especialidad,
            "docente_nombre": nombre_docente,
        },
    )

def _nivel_de_curso(nombre):
    coincidencia = re.match(r"^\s*([1-4])", nombre)
    return coincidencia.group(1) if coincidencia else ""

ESPECIALIDADES_TP = {
    "A": "Administración",
    "B": "Turismo",
    "C": "Electricidad",
    "D": "Gastronomía",
    "E": "Electrónica",
    "F": "Programación",
    "G": "Administración",
    "H": "Turismo",
    "I": "Electricidad",
    "J": "Gastronomía",
}

@login_required(login_url="login")
def horario_docente(request):
    _verificar_docente(request)

    perfil = request.user.perfil
    nombre_docente = perfil.nombre_completo or request.user.username

    clases = (
        ClaseHorario.objects
        .filter(docente__icontains=nombre_docente)
        .select_related("bloque")
        .order_by(
            "dia",
            "bloque__jornada",
            "bloque__orden",
            "bloque__hora_inicio",
        )
    )

    return render(
        request,
        "portales/docente/horario_docente.html",
        {
            "clases": clases,
            "nombre_docente": nombre_docente,
        },
    )

@login_required(login_url="login")
@require_POST
def limpiar_horario_curso(request):
    _verificar_administrador(request)

    curso = request.POST.get("curso", "").strip()

    if not curso:
        messages.error(request, "Selecciona un curso antes de limpiar.")
    else:
        cantidad = ClaseHorario.objects.filter(
            curso__iexact=curso
        ).count()

        ClaseHorario.objects.filter(curso__iexact=curso).delete()

        messages.success(
            request,
            f"Se eliminaron {cantidad} clases de {curso}. "
            "Los bloques y pausas se conservaron."
        )

    return redirect("gestionar_horarios")

def _etiqueta_curso(codigo):
    coincidencia = re.match(
        r"^\s*([1-4])\s*([A-J])\s*(.*)$",
        codigo,
        re.IGNORECASE,
    )

    if not coincidencia:
        return codigo

    nivel, paralelo, identificador = coincidencia.groups()
    paralelo = paralelo.upper()

    if nivel in {"1", "2"}:
        especialidad = "Formación General"
    else:
        especialidad = ESPECIALIDADES_TP.get(
            paralelo,
            "Especialidad técnica",
        )

    etiqueta = f"{paralelo} — {especialidad}"

    if identificador.strip():
        etiqueta += f" ({identificador.strip()})"

    return etiqueta

@login_required(login_url="login")
def gestionar_horarios(request):
    _verificar_administrador(request)
    vista = request.GET.get("vista", "horarios")
    if vista not in {"horarios", "cursos", "salas"}:
        vista = "horarios"

    cursos = list(
        ClaseHorario.objects
        .order_by("curso")
        .values_list("curso", flat=True)
        .distinct()
    )
    cursos = list(
        ClaseHorario.objects
        .order_by("curso")
        .values_list("curso", flat=True)
        .distinct()
    )

    cursos_catalogo = [
        "1A 410", "1B 410", "1C 410",
        "1A 510", "1B 510", "1C 510", "1D 510",
        "1A 610", "1B 610", "1C 610",

        "2A 410", "2B 410", "2C 410",
        "2A 510", "2B 510", "2C 510", "2D 510",
        "2A 610", "2B 610", "2C 610",

        "3A 410", "3B 410",
        "3A 510", "3B 510", "3C 510", "3D 510", "3E 510",
        "3A 610", "3B 610", "3C 610",

        "4A 410", "4B 410",
        "4A 510", "4B 510", "4C 510", "4D 510", "4E 510",
        "4A 610", "4B 610", "4C 610",
    ]

    niveles = [
        ("1", "1° Medio"),
        ("2", "2° Medio"),
        ("3", "3° Medio"),
        ("4", "4° Medio"),
    ]

    nivel_solicitado = request.GET.get("nivel", "")
    niveles_validos = [valor for valor, _ in niveles]
    nivel_seleccionado = (
        nivel_solicitado
        if nivel_solicitado in niveles_validos
        else (niveles_validos[0] if niveles_validos else "")
    )

    cursos_nivel = [
        curso for curso in cursos_catalogo
        if not nivel_seleccionado
        or _nivel_de_curso(curso) == nivel_seleccionado
    ]
    
    cursos_opciones = [
        {
            "codigo": curso,
            "etiqueta": _etiqueta_curso(curso),
        }
        for curso in cursos_nivel
    ]

    curso_solicitado = request.GET.get("curso", "").strip()
    curso_seleccionado = (
        curso_solicitado
        if curso_solicitado in cursos_nivel
        else (cursos_nivel[0] if cursos_nivel else "")
    )

    archivo_horario = (
        HorarioArchivo.objects.filter(curso=curso_seleccionado).first()
        if curso_seleccionado else None
    )

    jornadas = BloqueHorario.JORNADAS
    jornada_seleccionada = request.GET.get("jornada", "manana")

    if jornada_seleccionada not in ("manana", "tarde", "completa"):
        jornada_seleccionada = "manana"

    if jornada_seleccionada == "completa":
        bloques = list(
            BloqueHorario.objects.order_by(
                "jornada", "orden", "hora_inicio"
            )
        )

        clases = list(
            ClaseHorario.objects
            .filter(curso__iexact=curso_seleccionado)
            .select_related("bloque")
            .order_by("bloque__jornada", "dia", "grupo", "segmento")
        ) if curso_seleccionado else []
    else:
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

    cursos_tarjetas = []

    for nombre_curso in cursos:
        clases_curso = list(
            ClaseHorario.objects
            .filter(curso__iexact=nombre_curso)
            .select_related("bloque")
            .order_by("bloque__jornada", "bloque__orden")
        )

        if not clases_curso:
            continue

        primer_bloque = clases_curso[0].bloque
        docentes_curso = sorted({
            clase.docente.strip()
            for clase in clases_curso
            if clase.docente and clase.docente.strip()
        })

        cursos_tarjetas.append({
            "nombre": nombre_curso,
            "nivel": _nivel_de_curso(nombre_curso),
            "jornada": primer_bloque.jornada,
            "jornada_nombre": primer_bloque.get_jornada_display(),
            "bloques": len({clase.bloque_id for clase in clases_curso}),
            "docentes": docentes_curso,
        })

    matriz = []

    for bloque in bloques:
        fila = {
            "id": bloque.id,
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
                    "numero": numero_dia,
                    "nombre": nombre_dia,
                    "clases": tarjetas,
                })

        matriz.append(fila)

    clases_con_sala = list(
        ClaseHorario.objects
        .exclude(sala__isnull=True)
        .exclude(sala__exact="")
        .select_related("bloque")
        .order_by("sala", "dia", "bloque__orden")
    )

    salas_ocupadas_count = len({
        clase.sala.strip().casefold()
        for clase in clases_con_sala
    })

    return render(
        request,
        "portales/horarios/gestionar.html",
        {
            "bloques": bloques,
            "clases": clases,
            "matriz": matriz,
            "cursos": cursos_nivel,
            "cursos_tarjetas": cursos_tarjetas,
            "curso_seleccionado": curso_seleccionado,
            "jornadas": jornadas,
            "jornada_seleccionada": jornada_seleccionada,
            "niveles": niveles,
            "nivel_seleccionado": nivel_seleccionado,
            "vista": vista,
            "cursos_opciones": cursos_opciones,
            "clases_con_sala": clases_con_sala,
            "salas_ocupadas_count": salas_ocupadas_count,
            "archivo_horario": archivo_horario,
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
        "portales/horarios/formulario.html",
        {"form": form, "titulo": "Crear bloque horario"},
    )


@login_required(login_url="login")
def crear_clase_horario(request):
    _verificar_administrador(request)
    form = ClaseHorarioForm(
        request.POST or None,
        initial={
            "curso": request.GET.get("curso", ""),
            "dia": request.GET.get("dia", ""),
            "bloque": request.GET.get("bloque", ""),
        },
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La clase fue agregada al horario.")
        return redirect("gestionar_horarios")

    return render(
        request,
        "portales/horarios/formulario.html",
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
        "portales/horarios/formulario.html",
        {"form": form, "titulo": "Editar bloque horario"},
    )


@login_required(login_url="login")
@require_POST
def eliminar_bloque_horario(request, bloque_id):
    _verificar_administrador(request)
    bloque = get_object_or_404(BloqueHorario, pk=bloque_id)

    if bloque.clases.exists() or bloque.reservas.exists():
        messages.error(
            request,
            "No puedes eliminar este bloque porque tiene clases o reservas asignadas.",
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
        "portales/horarios/formulario.html",
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

@login_required(login_url="logear")
@require_POST
def cerrar_sesion_estudiante(request):
    logout(request)
    return redirect("logear")

@login_required(login_url="login")
def gestion_noticias(request):
    _verificar_administrador(request)

    todas_las_noticias = Noticia.objects.all()
    estado = request.GET.get("estado", "todas")

    noticias = todas_las_noticias

    if estado == "publicadas":
        noticias = noticias.filter(publicada=True)
    elif estado == "borradores":
        noticias = noticias.filter(publicada=False)
    else:
        estado = "todas"

    hoy = date.today()

    contexto = {
        "noticias": noticias,
        "estado_seleccionado": estado,
        "publicadas_count": todas_las_noticias.filter(publicada=True).count(),
        "borradores_count": todas_las_noticias.filter(publicada=False).count(),
        "total_count": todas_las_noticias.count(),
        "mes_count": todas_las_noticias.filter(
            fecha__month=hoy.month,
            fecha__year=hoy.year,
        ).count(),
    }

    return render(
        request,
        "portales/administracion/gestionar_noticias.html",
        contexto,
    )

@login_required(login_url="login")
def crear_noticia(request):
    _verificar_administrador(request)

    form = NoticiaForm(
        request.POST or None,
        request.FILES or None,
    )

    if request.method == "POST" and form.is_valid():
        noticia = form.save(commit=False)

        slug_base = slugify(noticia.titulo) or "noticia"
        noticia.slug = slug_base
        numero = 2

        while Noticia.objects.filter(slug=noticia.slug).exists():
            noticia.slug = f"{slug_base}-{numero}"
            numero += 1

        try:
            noticia.autor = request.user.perfil.nombre_completo
        except AttributeError:
            noticia.autor = request.user.username

        noticia.publicada = request.POST.get("accion") == "publicar"
        noticia.save()

        if noticia.publicada:
            messages.success(request, "La noticia fue publicada.")
        else:
            messages.success(request, "El borrador fue guardado.")

        return redirect("gestion_noticias")

    return render(
        request,
        "portales/administracion/crear_noticia.html",
        {"form": form},
    )

@login_required(login_url="login")
def editar_noticia(request, noticia_id):
    _verificar_administrador(request)

    noticia = get_object_or_404(Noticia, pk=noticia_id)
    form = NoticiaForm(
        request.POST or None,
        request.FILES or None,
        instance=noticia,
    )

    if request.method == "POST" and form.is_valid():
        noticia = form.save(commit=False)
        noticia.publicada = request.POST.get("accion") == "publicar"
        noticia.save()

        messages.success(request, "La noticia fue actualizada.")
        return redirect("gestion_noticias")

    return render(
        request,
        "portales/administracion/crear_noticia.html",
        {
            "form": form,
            "modo_edicion": True,
        },
    )

@login_required(login_url="login")
@require_POST
def cambiar_estado_noticia(request, noticia_id):
    _verificar_administrador(request)

    noticia = get_object_or_404(Noticia, pk=noticia_id)
    noticia.publicada = not noticia.publicada
    noticia.save(update_fields=["publicada"])

    messages.success(request, "El estado de la noticia fue actualizado.")
    return redirect("gestion_noticias")


@login_required(login_url="login")
@require_POST
def eliminar_noticia(request, noticia_id):
    _verificar_administrador(request)

    noticia = get_object_or_404(Noticia, pk=noticia_id)
    noticia.delete()

    messages.success(request, "La noticia fue eliminada.")
    return redirect("gestion_noticias")

@login_required(login_url="login")
def gestionar_reservas(request):
    _verificar_administrador(request)

    filtros = [
        ("pendiente", "Pendientes"),
        ("aprobada", "Aprobadas"),
        ("rechazada", "Rechazadas"),
        ("todas", "Todas"),
    ]
    estado = request.GET.get("estado", "pendiente")
    if estado not in dict(filtros):
        estado = "pendiente"

    base = ReservaEspacio.objects.select_related("docente__perfil", "bloque")
    conteos = {
        fila["estado"]: fila["total"]
        for fila in base.values("estado").annotate(total=Count("id"))
    }

    solicitudes = base if estado == "todas" else base.filter(estado=estado)
    if estado == "pendiente":
        solicitudes = solicitudes.order_by("fecha", "bloque__hora_inicio")

    solicitudes = list(solicitudes)
    for solicitud in solicitudes:
        solicitud.docente_nombre = _nombre_docente(solicitud.docente)

    return render(
        request,
        "portales/administracion/solicitudes_reserva.html",
        {
            "solicitudes": solicitudes,
            "filtros": filtros,
            "estado": estado,
            "total_pendientes": conteos.get("pendiente", 0),
            "total_aprobadas": conteos.get("aprobada", 0),
            "total_rechazadas": conteos.get("rechazada", 0),
        },
    )





def _redirigir_a_horario(curso):
    consulta = urlencode({
        "vista": "horarios",
        "nivel": _nivel_de_curso(curso),
        "curso": curso,
    })
    return redirect(f"{reverse('gestionar_horarios')}?{consulta}")


@login_required(login_url="login")
def subir_horario_archivo(request):
    _verificar_administrador(request)
    form = HorarioArchivoForm(
        request.POST or None,
        request.FILES or None,
        initial={"curso": request.GET.get("curso", "")},
    )

    if request.method == "POST" and form.is_valid():
        horario = form.guardar(request.user)
        messages.success(
            request,
            f"El horario de {horario.curso} fue publicado y ya aparece "
            "en la intranet de los estudiantes del curso.",
        )
        return _redirigir_a_horario(horario.curso)

    return render(
        request,
        "portales/horarios/formulario.html",
        {
            "form": form,
            "titulo": "Subir horario del curso",
            "ayuda": (
                "Elige el curso y sube el horario en PDF o PNG (máximo 10 MB). "
                "Si el curso ya tiene un horario, será reemplazado."
            ),
        },
    )


@login_required(login_url="login")
@require_POST
def eliminar_horario_archivo(request, pk):
    _verificar_administrador(request)
    horario = get_object_or_404(HorarioArchivo, pk=pk)
    curso = horario.curso
    horario.delete()
    messages.success(request, f"Se eliminó el horario en archivo de {curso}.")
    return _redirigir_a_horario(curso)


@login_required(login_url="login")
@xframe_options_sameorigin
def ver_horario_archivo(request, pk):
    """Entrega el archivo solo a administradores o a estudiantes del mismo curso."""
    horario = get_object_or_404(HorarioArchivo, pk=pk)

    if not _es_administrador(request.user):
        try:
            perfil = request.user.perfil
            permitido = (
                perfil.rol.nombre == "Estudiante"
                and (perfil.curso or "").strip().lower() == horario.curso.lower()
            )
        except AttributeError:
            permitido = False

        if not permitido:
            raise PermissionDenied

    try:
        archivo = horario.archivo.open("rb")
    except FileNotFoundError:
        raise Http404("El archivo del horario no está disponible.")

    tipo, _ = mimetypes.guess_type(horario.archivo.name)
    return FileResponse(
        archivo,
        content_type=tipo or "application/octet-stream",
        as_attachment=request.GET.get("descargar") == "1",
        filename=horario.nombre_descarga,
    )


def _nombre_docente(usuario):
    try:
        nombre = usuario.perfil.nombre_completo
    except AttributeError:
        nombre = ""
    return nombre or usuario.get_username()


def _parsear_fecha(texto):
    try:
        return date.fromisoformat((texto or "").strip())
    except ValueError:
        return None


def _volver_a_reservas(espacio, fecha):
    consulta = {}
    if espacio in dict(ReservaEspacio.ESPACIOS):
        consulta["espacio"] = espacio
    if fecha:
        consulta["semana"] = (fecha - timedelta(days=fecha.weekday())).isoformat()
    destino = reverse("reservar_espacios")
    return redirect(f"{destino}?{urlencode(consulta)}" if consulta else destino)


@login_required(login_url="login")
@require_POST
def solicitar_reserva(request):
    _verificar_docente(request)
    form = SolicitudReservaForm(request.POST, docente=request.user)

    if form.is_valid():
        datos = form.cleaned_data
        try:
            with transaction.atomic():
                ReservaEspacio.objects.create(
                    docente=request.user,
                    espacio=datos["espacio"],
                    fecha=datos["fecha"],
                    bloque=datos["bloque"],
                    motivo=datos["motivo"],
                )
        except IntegrityError:
            messages.error(
                request,
                "No se pudo registrar la solicitud: el bloque ya no está disponible.",
            )
        else:
            messages.success(
                request,
                "Solicitud enviada. Quedó pendiente de aprobación por Administración.",
            )
    else:
        for errores in form.errors.values():
            for error in errores:
                messages.error(request, error)

    return _volver_a_reservas(
        request.POST.get("espacio", ""),
        _parsear_fecha(request.POST.get("fecha")),
    )


@login_required(login_url="login")
@require_POST
def cancelar_reserva(request, pk):
    _verificar_docente(request)
    reserva = get_object_or_404(ReservaEspacio, pk=pk, docente=request.user)

    if reserva.estado in {"pendiente", "aprobada"} and reserva.fecha >= timezone.localdate():
        reserva.estado = "cancelada"
        reserva.save(update_fields=["estado"])
        messages.success(request, "La reserva fue cancelada.")
    else:
        messages.error(request, "Esta reserva ya no se puede cancelar.")

    return _volver_a_reservas(reserva.espacio, reserva.fecha)


def _volver_a_solicitudes(request):
    estado = request.POST.get("estado_filtro", "pendiente")
    if estado not in {"pendiente", "aprobada", "rechazada", "todas"}:
        estado = "pendiente"
    return redirect(f"{reverse('gestionar_reservas')}?{urlencode({'estado': estado})}")


@login_required(login_url="logear")
@require_POST
def aprobar_reserva(request, pk):
    _verificar_administrador(request)

    with transaction.atomic():
        reserva = get_object_or_404(
            ReservaEspacio.objects.select_for_update(), pk=pk,
        )

        if reserva.estado != "pendiente":
            messages.error(request, "Esta solicitud ya fue revisada.")
        elif reserva.fecha < timezone.localdate():
            messages.error(request, "La fecha de esta solicitud ya pasó.")
        elif ReservaEspacio.objects.filter(
            espacio=reserva.espacio,
            fecha=reserva.fecha,
            bloque=reserva.bloque,
            estado="aprobada",
        ).exclude(pk=reserva.pk).exists():
            messages.error(
                request,
                "Ese bloque ya fue aprobado para otro docente.",
            )
        else:
            ahora = timezone.now()
            reserva.estado = "aprobada"
            reserva.revisada_por = request.user
            reserva.revisada_en = ahora
            reserva.save()

            descartadas = (
                ReservaEspacio.objects
                .filter(
                    espacio=reserva.espacio,
                    fecha=reserva.fecha,
                    bloque=reserva.bloque,
                    estado="pendiente",
                )
                .exclude(pk=reserva.pk)
                .update(
                    estado="rechazada",
                    revisada_por=request.user,
                    revisada_en=ahora,
                    comentario_admin="El espacio fue asignado a otro docente.",
                )
            )

            mensaje = (
                f"Reserva aprobada para {_nombre_docente(reserva.docente)}. "
                "Ya aparece en su horario de reservas."
            )
            if descartadas:
                mensaje += f" Se rechazaron {descartadas} solicitud(es) en conflicto."
            messages.success(request, mensaje)

    return _volver_a_solicitudes(request)


@login_required(login_url="logear")
@require_POST
def rechazar_reserva(request, pk):
    _verificar_administrador(request)
    reserva = get_object_or_404(ReservaEspacio, pk=pk)

    if reserva.estado != "pendiente":
        messages.error(request, "Esta solicitud ya fue revisada.")
    else:
        reserva.estado = "rechazada"
        reserva.revisada_por = request.user
        reserva.revisada_en = timezone.now()
        reserva.comentario_admin = request.POST.get("comentario", "").strip()[:200]
        reserva.save()
        messages.success(request, "La solicitud fue rechazada.")

    return _volver_a_solicitudes(request)

def atender_solicitud_recuperacion(request, solicitud_id):
    if request.method != "POST":
        return redirect("listar_solicitudes_recuperacion")

    solicitud = get_object_or_404(SolicitudRecuperacion, id=solicitud_id)
    usuario = solicitud.usuario  # Ajusta si el campo se llama distinto en tu modelo

    ok, mensaje = procesar_recuperacion_usuario(usuario)

    if ok:
        # Ajusta según cómo guardes el estado en tu modelo de portales
        solicitud.estado = "atendida"
        solicitud.save()
        messages.success(request, mensaje)
    else:
        messages.error(request, mensaje)

    return redirect("listar_solicitudes_recuperacion")

