# 🏫 Sistema de Gestión y Horarios - Liceo Antonio Varas de la Barra

<div align="center">

![Status](https://img.shields.io/badge/Status-En%20Desarrollo-brightgreen?style=for-the-badge)
![Scrum](https://img.shields.io/badge/Metodología-Scrum-blue?style=for-the-badge)
![Tecnología](https://img.shields.io/badge/Stack-FullStack-orange?style=for-the-badge)
![Identidad](https://img.shields.io/badge/UI-%23071936%20%26%20%23f5a800-071936?style=for-the-badge)

</div>

---

## 👥 Equipo de Desarrollo

| Integrante | Rol / Contribución |
| :--- | :--- |
| **Marjorie Gómez** | esarrollo web institucional e intranet trazabilidad de HUs |
| **Alison Limachi** | Panel de administración, módulos de gestión , plantillas administrativas |
| **Lucas Muñoz** | Panel de usuarios |

---

## 🚀 Planificación y Sprints (Backlog del Producto)

El desarrollo del sistema se encuentra organizado de forma modular a través de iteraciones Scrum, combinando componentes del portal institucional, módulos de administración y las historias de usuario revisadas en el tablero:

# 🏫 Trazabilidad de Historias de Usuario - Módulo Intranet y Administración

Este documento detalla la correspondencia técnica y funcional entre los componentes desarrollados en el frontend/backend y las Historias de Usuario (HUs) trabajadas en el proyecto para el **Liceo Bicentenario de Excelencia Antonio Varas de la Barra**.

---

## 🔐 1. Sprint 1: Análisis, Auth & Consultas
*Garantizar el acceso seguro de los usuarios según su rol, proteger datos sensibles y permitir la consulta centralizada de horarios y salidas.*

| ID | Historia de Usuario | Componente / Vista Asociada | Descripción Funcional | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **SCRUM-5** | **HU01: Autenticación dual de usuarios** | `base.html` (Navbar / Acceso) | Diferenciación del acceso seguro según el rol institucional (estudiante, docente, UTP o inspectoría). | ✅ Done |
| **SCRUM-6** | **HU02: Gestión de roles y permisos** | `base.html` / Control de Sesión | Restricción de navegación y vistas según los privilegios del usuario autenticado. | ✅ Done |
| **SCRUM-7** | **HU03: Consulta centralizada de horarios** | `index.html` (Estructura Base) | Punto de partida para que la comunidad escolar consulte la información general y horarios. | ✅ Done |
| **SCRUM-9** | **HU05: Recuperación autoservicio de clave** | Módulo de Acceso / Seguridad | Flujo de recuperación de credenciales de acceso para usuarios del portal. | ✅ Done |
| **SCRUM-15** | **HU11: Consulta de salidas diarias** | `footer.html` / Accesos Institucionales | Visualización de flujos y horarios de salida diarios de los alumnos. | ✅ Done |
| **SCRUM-34** | **HU30: Anonimización y protección de datos sensibles** | Seguridad / Privacidad | Resguardo de información personal y sensible dentro del portal. | ✅ Done |
| **SCRUM-10** | **HU06: Detalle de electivos y talleres** | `especialidades.html` | Muestra estructurada de perfiles, módulos clave y campos laborales de la formación técnica. | ✅ Documentada |

---

## ⚙️ 2. Sprint 2: Gestión, Claves & Control
*Habilitar la edición dinámica y carga masiva de horarios, asignación de reemplazos, avisos de jornada y trazabilidad administrativa.*

| ID | Historia de Usuario | Componente / Backend Asociado | Descripción Funcional | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **SCRUM-8** | **HU04: Edición dinámica de horarios** | Módulo UTP | Gestión ágil de la matriz horaria directamente desde el panel de administración. | ✅ Done |
| **SCRUM-19** | **HU15: Carga masiva de horarios vía Excel/CSV** | Motor de Importación UTP | Actualización masiva de parrillas académicas reflejadas en el sistema. | ✅ Done |
| **SCRUM-27** | **HU23: Configuración de vigencia de contraseñas** | Seguridad / Panel Admin | Reglas y control de expiración/vigencia para las claves de acceso. | ✅ Done |
| **SCRUM-14** | **HU10: Registro de auditoría y cambios (Logs)** | `registro_auditoria` (`admin_auditoria.html`) | Registro histórico de acciones y modificaciones realizadas en el sistema. | 🔄 In Progress |
| **SCRUM-16** | **HU12: Registro de suspensiones y avisos de jornada** | `suspensiones_jornada` (`admin_suspensiones.html`) | Publicación y registro de suspensiones de clases, ajustes o avisos de jornada. | 🔄 In Progress |
| **SCRUM-21** | **HU17: Asignación temporal de profesores reemplazantes** | `asignar_reemplazos` (`admin_reemplazos.html`) | Registro de reemplazos docentes temporales vinculados a curso, asignatura y vigencia. | 🔄 In Progress |
| **SCRUM-29** | **HU25: Justificación obligatoria de cambios de horario** | Validación en `asignar_reemplazos` y `cambios_sala` | Exigencia de motivo/justificación obligatoria al registrar cambios o reemplazos. | 🔄 In Progress |

---

## 🗺️ 3. Sprint 3: Recintos, Wayfinding & Reservas
*Implementación del módulo de gestión de recintos, reservas, disponibilidad y monitoreo espacial.*

| ID | Historia de Usuario | Módulo / Enlace Conceptual | Descripción Funcional | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **SCRUM-11** | **HU07: Reserva digital de espacios comunes** | Módulo de Infraestructura | Solicitud digital de salas, laboratorios y recintos compartidos. | ✅ Done |
| **SCRUM-12** | **HU08: Validación de cruces en reservas** | Motor de Restricciones | Prevención automática de superposiciones en reservas de salas. | ✅ Done |
| **SCRUM-22** | **HU18: Gestión y aprobación de reservas de recintos** | Panel de Administración | Gestión y validación de solicitudes de espacios físicos. | ✅ Done |
| **SCRUM-23** | **HU19: Parametrización de salas y equipamiento** | Configuración de Equipamiento | Registro de capacidades, recursos y características por espacio. | ✅ Done |
| **SCRUM-25** | **HU21: Búsqueda de salas y espacios desocupados** | Filtros de Disponibilidad | Localización rápida de salas y espacios libres en tiempo real. | ✅ Done |
| **SCRUM-13** | **HU09: Mapa de orientación digital** | Catálogos Institucionales | Vinculación visual de dependencias, pabellones y especialidades dentro del recinto. | ✅ Documentada |
| **SCRUM-28** | **HU24: Monitoreo por pabellón** | Panel Visual General | Estado de ocupación física de las instalaciones del establecimiento. | ✅ Documentada |

---

## 🛠️ 4. Sprint 4: TP e Inspectoría
*Optimización de la operación diaria mediante filtros especializados, rotación de talleres, cambios de sala, exportación y control de salidas.*

| ID | Historia de Usuario | Componente Asociado | Descripción Funcional | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **SCRUM-17** | **HU13: Identificación visual de profesores volantes** | Parrilla / Gestión Docente | Señalización visual para distinguir docentes volantes en la planificación. | ✅ Done |
| **SCRUM-18** | **HU14: Coordinación horaria y articulación PIE** | Apoyo Pedagógico | Sincronización de horarios de integración escolar y apoyos docentes. | ✅ Done |
| **SCRUM-20** | **HU16: Exportación de horario semanal a PDF** | Exportación / Horarios | Generación y descarga del horario semanal en formato PDF. | ✅ Done |
| **SCRUM-30** | **HU26: Filtro de parrilla por especialidad técnica** | `especialidades.html` / Parrilla TP | Desglose y segmentación de horarios por especialidad TP. | ✅ Done |
| **SCRUM-31** | **HU27: Búsqueda rápida de docentes por ubicación** | Consulta / Parrilla | Localización rápida de docentes según sala o espacio asignado. | ✅ Done |
| **SCRUM-24** | **HU20: Notificación de cambio de sala de última hora** | `cambios_sala` (`admin_cambios_sala.html`) | Registro y notificación de reubicaciones inmediatas de sala o laboratorio con justificación. | 🔄 In Progress |
| **SCRUM-26** | **HU22: Programación de rotación de grupos en talleres** | `rotacion_talleres` (`admin_rotacion_talleres.html`) | Programación de turnos y rotaciones de grupos entre talleres y espacios prácticos. | 🔄 In Progress |
| **SCRUM-33** | **HU29: Generación de planilla diaria de control de salidas** | `control_salidas` (`admin_control_salidas.html`) | Registro diario e impresión de salidas de estudiantes, docentes o funcionarios. | 🔄 In Progress |

---