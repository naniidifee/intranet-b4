# 🏫 Sistema de Gestión y Horarios - Liceo Antonio Varas de la Barra

<div align="center">

![Status](https://img.shields.io/badge/Status-En%20Desarrollo-brightgreen?style=for-the-badge)
![Scrum](https://img.shields.io/badge/Metodología-Scrum-blue?style=for-the-badge)
![Tecnología](https://img.shields.io/badge/Stack-FullStack-orange?style=for-the-badge)

</div>

---

## 👥 Equipo de Desarrollo

| Integrante | Rol / Contribución |
| :--- | :--- |
| **Marjorie Gómez** | 
| **Alison Limachi** | 
| **Lucas Muñoz** | 

---

## 🚀 Planificación y Sprints (Backlog del Producto)

El desarrollo del sistema se encuentra organizado de forma modular a través de iteraciones Scrum:

# 🏫 Trazabilidad de Historias de Usuario - Módulo Intranet

Este documento detalla la correspondencia técnica y funcional entre los componentes desarrollados en el frontend/backend (`base.html`, `index.html`, `footer.html`, `especialidades.html`) y las Historias de Usuario (HUs) del backlog del proyecto para el **Liceo Bicentenario de Excelencia Antonio Varas de la Barra**.

---

## 🔐 1. Sprint 1: Auth & Consultas
*Garantizar el acceso seguro de los usuarios según su rol y permitir la consulta centralizada de horarios y salidas.*

| ID | Historia de Usuario | Componente / Vista Asociada | Descripción Funcional |
| :--- | :--- | :--- | :--- |
| **SCRUM-5** | **HU01: Autenticación dual** | `base.html` (Navbar / Acceso) | Diferenciación del acceso seguro según el rol institucional (estudiante, docente, UTP o inspectoría). |
| **SCRUM-6** | **HU02: Gestión de roles y permisos** | `base.html` / Control de Sesión | Restricción de navegación y vistas según los privilegios del usuario autenticado. |
| **SCRUM-7** | **HU03: Consulta centralizada de horarios** | `index.html` (Estructura Base) | Punto de partida para que la comunidad escolar consulte la información general y horarios. |
| **SCRUM-15** | **HU11: Consulta de salidas diarias** | `footer.html` / Accesos Institucionales | Visualización de flujos y horarios de salida diarios de los alumnos. |
| **SCRUM-10** | **HU06: Detalle de electivos y talleres** | `especialidades.html` | Muestra estructurada de perfiles, módulos clave y campos laborales de la formación técnica. |

---

## ⚙️ 2. Sprint 2: Gestión & Claves
*Habilitar la edición dinámica y carga masiva de horarios, asegurando trazabilidad y control administrativo.*

| ID | Historia de Usuario | Componente / Backend Asociado | Descripción Funcional |
| :--- | :--- | :--- | :--- |
| **SCRUM-8** | **HU04: Edición dinámica de horarios** | Módulo UTP | Gestión ágil de la matriz horaria directamente desde el panel de administración. |
| **SCRUM-19** | **HU15: Carga masiva (Excel/CSV)** | Motor de Importación UTP | Actualización masiva de parrillas académicas reflejadas de forma automática en el frontend. |
| **SCRUM-14** | **HU10: Auditoría y cambios (Logs)** | Sistema de Trazabilidad | Registro histórico de modificaciones realizadas sobre las parrillas académicas. |
| **SCRUM-29** | **HU25: Justificación de cambios** | Validación de Cambios UTP | Requisito administrativo obligatorio al modificar la planificación horaria. |

---

## 🗺️ 3. Sprint 3: Recintos, Wayfinding & Reservas
*Implementación del módulo de orientación espacial, gestión y monitoreo de ocupación.*

| ID | Historia de Usuario | Módulo / Enlace Conceptual | Descripción Funcional |
| :--- | :--- | :--- | :--- |
| **SCRUM-13** | **HU09: Mapa de orientación digital** | Catálogos Institucionales | Vinculación visual de dependencias, pabellones y especialidades dentro del recinto. |
| **SCRUM-11** | **HU07: Reserva de espacios comunes** | Módulo de Infraestructura | Solicitud digital de salas, laboratorios y recintos compartidos. |
| **SCRUM-12** | **HU08: Validación de cruces** | Motor de Restricciones | Prevención automática de superposiciones en reservas de salas. |
| **SCRUM-22** | **HU18: Aprobación de reservas** | Panel de Administración | Gestión y validación de solicitudes de espacios físicos. |
| **SCRUM-23** | **HU19: Parametrización de salas** | Configuración de Equipamiento | Registro de capacidades, recursos y características por espacio. |
| **SCRUM-25** | **HU21: Búsqueda de desocupados** | Filtros de Disponibilidad | Localización rápida de salas y espacios libres en tiempo real. |
| **SCRUM-28** | **HU24: Monitoreo por pabellón** | Panel Visual General | Estado de ocupación física de las instalaciones del establecimiento. |

---

## 🛠️ 4. Sprint 4: TP e Inspectoría
*Optimización de la operación diaria mediante filtros especializados y control de asistencia.*

| ID | Historia de Usuario | Componente Asociado | Descripción Funcional |
| :--- | :--- | :--- | :--- |
| **SCRUM-30** | **HU26: Filtro por especialidad técnica** | `especialidades.html` / Parrilla TP | Desglose y segmentación de horarios por especialidad (Administración, Programación, Electricidad, Electrónica, Gastronomía y Turismo). |
| **SCRUM-33** | **HU29: Planilla diaria de control de salidas** | `footer.html` / Inspectoría | Soporte operativo para el registro y validación de salidas de estudiantes. |
| **SCRUM-18** | **HU14: Coordinación horaria y PIE** | Apoyo Pedagógico | Sincronización de horarios de integración escolar y apoyos docentes. |