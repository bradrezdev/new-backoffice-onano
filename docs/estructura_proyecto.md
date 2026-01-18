# Estructura del Proyecto y Plan de Reorganización

**Fecha:** 18 de enero de 2026
**Autores:** Project Manager Expert, Reflex UI Architect, Python Backend Architect
**Objetivo:** Limpieza profunda y reestructuración de Arquitectura de Software.

---

## 1. Diagnóstico del Estado Actual ("Los Pies y la Cabeza")

Tras auditar tu espacio de trabajo, hemos llegado a una conclusión clara: **Tu proyecto tiene un núcleo sólido ("Vertical Slice Architecture"), pero está enterrado bajo una capa masiva de desorden administrativo en la raíz.**

### El Problema Principal: "La Zona de Guerra en la Raíz"
Actualmente, tu carpeta raíz (`/`) tiene más de **50 archivos sueltos** que mezclan propósitos. Tienes scripts de pruebas (`test_...`), scripts de corrección (`fix_...`), scripts de análisis (`check_...`) y documentación dispersa mezclados con los archivos vitales de arranque. Esto hace imposible saber qué es código en producción y qué es basura de desarrollo.

### El Problema Secundario: Inconsistencia en `NNProtect_new_website/`
Dentro de la carpeta de la aplicación, hay un intento de organizar por "Servicios" (`ordering`, `mlm`, `finance`), lo cual es **excelente**. Sin embargo, es inconsistente:
- Tienes una carpeta `auth/` y otra `auth_service/`.
- Tienes una carpeta `pages/` que está vacía (solo tiene `__init__.py`).
- Las "Páginas" (UI) están mezcladas dentro de las carpetas de "Servicios". Esto no es malo (es Arquitectura Vertical), pero si no se define una regla clara, se vuelve confuso.

---

## 2. Arquitectura Propuesta: "Reflex Modular Vertical"

Para un sistema MLM (Multinivel) que incluye Tienda, Oficina Virtual, Billetera y Administración, la estructura clásica de "Frontend/Backend" no es suficiente.

Hemos diseñado una **Arquitectura Modular Vertical**. En lugar de separar por tipo de archivo (todas las páginas juntas, todos los estados juntos), separaremos por **MÓDULO DE NEGOCIO**.

### Principios
1.  **Limpieza Radical:** La raíz solo debe tener configuración y arranque.
2.  **Módulos Autónomos:** Todo lo relacionado con "Tienda" (UI, Estado, Lógica de BD) vive en la carpeta `store`. Todo lo de "Comisiones" vive en `network`.
3.  **Shared (Compartido):** Solo lo que usan todos (UI base, conexión a DB, utilidades) va a carpetas comunes.

---

## 3. Mapa de la Nueva Estructura (Target)

A continuación, el detalle de dónde debe ir cada pieza.

### A. Nivel Raíz (Limpieza Total)
*Solo deben quedar los archivos esenciales para que el proyecto arranque y se configure.*

```text
/Users/bradrez/Documents/NNProtect_new_website/
├── scripts/                 <-- NUEVA: Aquí mueves TODOS los scripts sueltos
│   ├── tests/               <-- Mover aquí todos los test_*.py
│   ├── maintenance/         <-- Mover aquí fix_*.py, check_*.py, update_*.py
│   ├── data_seeding/        <-- Mover aquí create_*.py, seed_*.py
│   └── analysis/            <-- Mover aquí analyze_*.py, debug_*.py
├── docs/                    <-- Mover aquí todos los .md (excepto README)
├── requirements.txt         <-- Dependencias
├── rxconfig.py              <-- Configuración de Reflex
├── alembic.ini              <-- Configuración de BBDD
└── NNProtect_new_website/   <-- EL NÚCLEO DEL PROGRAMA