# Estructura del Proyecto y Plan de Reorganización

**Fecha:** 18 de enero de 2026
**Autores:** Project Manager Expert, Reflex UI Architect, Python Backend Architect
**Objetivo:** Definir la Arquitectura Modular Estandarizada para todo el sistema.

---

## 1. El Estándar de Oro: "Arquitectura Modular Vertical"

Para evitar confusiones futuras y re-trabajo, hemos definido una **regla inquebrantable** para la estructura de cada módulo. Ya no habrá módulos "simples" o "complejos" con estructuras diferentes. **Todos seguirán el mismo patrón.**

### ¿Por qué la distinción anterior?
Originalmente, `auth` se dejó plano porque solo tenía 2 archivos de lógica. `store` se pidió subdivido porque tiene docenas. **Esto fue un error de inconsistencia.** Para tu tranquilidad y orden mental, estandarizaremos todo bajo el modelo de "4 Capas".

---

## 2. Estructura de un Módulo Estándar

Cada carpeta dentro de `modules/` (**auth, store, network, finance, admin**) DEBE tener estas 4 subcarpetas internas. Si un módulo es pequeño y solo tiene un archivo, igual se respeta la carpeta.

```text
modules/
└── {nombre_del_modulo}/
    ├── pages/          <-- LA CARA: Archivos UI accesibles por URL.
    │                       (Ej: store.py, login.py, dashboard.py)
    │
    ├── components/     <-- LOS BRAZOS: Partes de UI reusables solo aquí.
    │                       (Ej: product_card.py, genealogy_node.py)
    │
    ├── state/          <-- EL CEREBRO DE UI: Lógica interactiva de Reflex.
    │                       (Ej: store_state.py, auth_state.py)
    │
    └── backend/        <-- EL MOTOR: Lógica pura, DB y cálculos (Sin Reflex).
                            (Ej: order_service.py, commission_calc.py)
```

---

## 3. Mapa del Proyecto Completo (Visión Futura Final)

Así es como se verá tu proyecto cuando terminemos la reestructuración. Úsalo como guía para saber dónde poner cada nuevo archivo.

### A. Raíz (Infraestructura)
```text
/Users/bradrez/Documents/NNProtect_new_website/
├── scripts/                 <-- Mantenimiento, Tests, Seeds y Análisis
├── docs/                    <-- Documentación
├── requirements.txt         <-- Dependencias
├── rxconfig.py              <-- Configuración
└── NNProtect_new_website/   <-- CÓDIGO FUENTE
```

### B. Núcleo (`NNProtect_new_website/`)

```text
/NNProtect_new_website/
├── NNProtect_new_website.py  <-- Router Principal (App Entry Point)
├── state.py                  <-- Estado Base (Global)
│
├── components/               <-- UI COMPARTIDA (Usada por >1 módulo)
│   ├── layout.py             (Sidebars, Headers)
│   ├── theme.py              (Colores, Estilos)
│   └── tables.py             (Estilos de tablas genéricos)
│
├── modules/                  <-- LOS MÓDULOS DE NEGOCIO
│   │
│   ├── auth/                 <-- [Módulo de Identidad]
│   │   ├── pages/            (login.py, register.py, welcome.py)
│   │   ├── components/       (register_form.py, login_card.py)
│   │   ├── state/            (auth_state.py)
│   │   └── backend/          (auth_service.py - Conexión Supabase)
│   │
│   ├── store/                <-- [Módulo Comercial]
│   │   ├── pages/            (store.py, cart.py, orders.py, payment.py)
│   │   ├── components/       (product_card.py, cart_summary.py)
│   │   ├── state/            (store_state.py, cart_state.py)
│   │   └── backend/          (product_queries.py, order_processing.py)
│   │
│   ├── network/              <-- [Módulo MLM] (Antes mlm_service)
│   │   ├── pages/            (tree.py, network_reports.py)
│   │   ├── components/       (tree_visualizer.py)
│   │   ├── state/            (network_state.py)
│   │   └── backend/          (commission_engine.py, tree_logic.py)
│   │
│   ├── finance/              <-- [Módulo Financiero]
│       ├── pages/            (wallet.py, withdrawals.py)
│       ├── components/       (balance_card.py)
│       ├── state/            (finance_state.py)
│       └── backend/          (payout_service.py)
│
└── utils/                    <-- HERRAMIENTAS PURAS (Python Helpers)
    ├── formatters.py
    └── validators.py
```

---

## 4. Plan de Acción Actualizado

1.  **Terminar Migración `store`:** Mover todo a las 4 capas (`pages`, `components`, `state`, `backend`).
2.  **Refactorizar `auth`:** Corregir "el módulo simple" creando las carpetas faltantes (`state`, `backend`) y moviendo los archivos.
3.  **Migrar `network` y `finance`:** Aplicar este molde exacto.

Esta estructura es "Aburrida" en el buen sentido: es predecible. Nunca tendrás que adivinar dónde va un archivo nuevo.
