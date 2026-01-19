# CLAUDE.md - Estado Actual del Proyecto NNProtect Backoffice

Este archivo proporciona orientación actualizada a Claude Code (claude.ai/code) sobre el **estado REAL** del proyecto NNProtect Backoffice MLM al momento de la entrega al nuevo equipo de desarrollo.

---

## 📋 Información General del Proyecto

**NNProtect Backoffice** es un sistema de gestión Multi-Level Marketing (MLM) construido con Reflex (Python web framework) y Supabase (PostgreSQL). La plataforma permite a los usuarios gestionar su negocio MLM incluyendo autenticación, referidos, compra de productos, gestión automática de rangos, cálculo de comisiones y reportes de red en tiempo real.

**Tecnologías:**
- Frontend: Reflex 0.6+ (Python reactive web framework)
- Backend: Python 3.11+
- Database: Supabase (PostgreSQL)
- Auth: Supabase Auth + JWT híbrido
- ORM: SQLModel
- Migraciones: Alembic
- Timezone: UTC storage con conversión México Central
- Scheduler: APScheduler para tareas automáticas

**Versión Actual:** 2.0.0 (Beta en Testing)
**Última Actualización:** Octubre 1, 2025
**Estado:** Entregado al equipo de desarrollo para continuación

---

## 🏗️ Arquitectura: 5 Servicios Principales

El proyecto está organizado en 5 servicios principales claramente definidos:

### 1️⃣ SERVICIO DE AUTENTICACIÓN
### 2️⃣ SERVICIO DE TIENDA
### 3️⃣ SERVICIO DE ÓRDENES
### 4️⃣ SERVICIO DE PAGOS
### 5️⃣ SERVICIO MULTINIVEL (MLM)

---

## 1️⃣ SERVICIO DE AUTENTICACIÓN

**Directorio:** `NNProtect_new_website/auth_service/`
**Estado:** ✅ 100% IMPLEMENTADO Y FUNCIONAL

### Archivos Clave
- `auth_state.py` - Estado global de autenticación con Reflex
- `supabase_auth_manager.py` - Gestión de Supabase Auth
- `supabase_client.py` - Cliente de Supabase

### Funcionalidades Implementadas
✅ **Login con JWT**
- Autenticación híbrida: Supabase Auth + JWT personalizado
- Tokens con expiración de 60 minutos
- Validación automática en cada request
- Método: `AuthenticationManager.create_jwt_token()`

✅ **Registro de Usuarios**
- Registro con sponsor obligatorio (via `?ref=member_id`)
- Registro sin sponsor (solo para primeros usuarios)
- Validación de sponsor antes de crear cuenta
- Creación automática de credenciales legacy + Supabase Auth

✅ **Carga de Datos Completos**
- `AuthState.load_user_from_token()`: Carga datos completos al montar página
- Usa `MLMUserManager.load_complete_user_data()` para completitud
- Incluye: PV/PVG cache, rango actual, rango máximo, sponsor, wallet balance
- Fallback a `_build_basic_profile_data()` si no hay Supabase ID

✅ **Gestión de Sesiones**
- Estado reactivo con `AuthState` (Reflex State)
- Redirección automática si no autenticado
- Logout con limpieza de cookies
- `profile_data`: Dict con todos los datos del usuario

### Páginas de Autenticación
Directorio: `NNProtect_new_website/auth/`
- `login.py` - Página de inicio de sesión
- `new_register.py` - Registro con sponsor
- `register_noSponsor.py` - Registro sin sponsor (admin)
- `welcome_page.py` - Página de bienvenida post-registro

### Modelos de Base de Datos
Directorio: `database/`
- `users.py` - Usuarios con member_id, sponsor_id, pv_cache, pvg_cache
- `auth_credentials.py` - Credenciales legacy (email/password hashed)
- `userprofiles.py` - Perfiles con datos personales
- `roles.py` + `roles_users.py` - Sistema de roles (no implementado totalmente)
- `social_accounts.py` - Cuentas sociales (futuro)

### Estado de Implementación
| Feature | Estado | Notas |
|---------|--------|-------|
| Login JWT | ✅ 100% | Funcional |
| Registro con Sponsor | ✅ 100% | Validación completa |
| Supabase Auth | ✅ 90% | Integrado pero no usado al 100% |
| Estado Global AuthState | ✅ 100% | Reactivo y funcional |
| Roles y Permisos | ⚠️ 50% | Tablas creadas, lógica no implementada |
| 2FA | ❌ 0% | No implementado |

### Próximos Pasos para el Equipo
1. ⚠️ **CRÍTICO**: Implementar sistema completo de roles y permisos para Admin Panel
2. Migrar completamente de AuthCredentials legacy a Supabase Auth
3. Implementar 2FA con Supabase Auth
4. Agregar password reset vía email
5. Implementar social login (Google, Facebook)

---

## 2️⃣ SERVICIO DE TIENDA

**Directorio:** `NNProtect_new_website/product_service/`
**Estado:** ✅ 90% IMPLEMENTADO Y FUNCIONAL

### Archivos Clave
- `store.py` - Página principal de la tienda
- `shopping_cart.py` - Carrito de compras funcional
- `store_products_state.py` - Estado reactivo del carrito (CountProducts)
- `store_state.py` - Estado general de tienda
- `product_manager.py` - Manager POO para productos
- `product_components.py` - Componentes UI reutilizables
- `product_data/product_data_service.py` - Servicio de datos de productos

### Funcionalidades Implementadas
✅ **Catálogo de Productos**
- 24 productos reales cargados en BD desde CSV
- Precios multi-país: México, USA, Colombia, República Dominicana
- Puntos de Volumen (PV) por país
- Valor Neto (VN) por país para comisiones
- Presentaciones: Kit, Líquido, Cápsulas, Skincare
- Tipos: Suplemento, Skincare, Desinfección

✅ **Carrito de Compras**
- Agregar/eliminar productos
- Cálculo automático de subtotal, envío, total
- Cálculo de puntos de volumen (PV) acumulados
- Estado reactivo global (CountProducts)
- Persistencia en sesión
- UI responsive móvil-primero

✅ **Gestión de Productos**
- ProductManager con método `get_products_by_country()`
- Detección automática de país del usuario
- Filtrado por categoría y tipo
- Badge "Nuevo" para productos recientes

### Modelos de Base de Datos
Directorio: `database/`
- `products.py` - Productos con campos:
  - `product_name`, `SKU`, `description`
  - `presentation` (kit/líquido/cápsulas)
  - `type` (suplemento/skincare/desinfección)
  - `pv_mx`, `pv_usa`, `pv_colombia` (Puntos de Volumen)
  - `vn_mx`, `vn_usa`, `vn_colombia` (Valor Neto)
  - `price_mx`, `price_usa`, `price_colombia` (Precio distribuidor)
  - `public_mx`, `public_usa`, `public_colombia` (Precio público)
  - `is_new` (badge nuevo)

### Estado de Implementación
| Feature | Estado | Notas |
|---------|--------|-------|
| Catálogo de Productos | ✅ 100% | 24 productos reales |
| Carrito Funcional | ✅ 100% | Agregar/eliminar funcionando |
| Cálculo de PV | ✅ 100% | Por país correcto |
| Precios Multi-País | ✅ 100% | MX, USA, COL, RD |
| UI Responsive | ✅ 100% | Móvil-primero |
| Búsqueda de Productos | ❌ 0% | No implementado |
| Filtros Avanzados | ⚠️ 30% | Solo categorías básicas |
| Wishlist | ❌ 0% | No implementado |
| Reviews | ❌ 0% | No implementado |

### ⚠️ PROBLEMAS IDENTIFICADOS
1. **NO existe distinción Kit vs Producto**:
   - Los kits deben generar PV pero NO VN
   - Los productos regulares generan PV y VN
   - **CRÍTICO para cálculo de comisiones**
   - ✅ Solución: Agregar campo `is_kit` y `generates_vn` en tabla Products

2. **Falta campo `stock` en productos**: Sin control de inventario

3. **No hay tabla de imágenes**: Solo 1 imagen por producto (campo `image_url` no existe en schema actual)

### Próximos Pasos para el Equipo
1. ⚠️ **URGENTE**: Implementar distinción Kit vs Producto (campo `is_kit`)
2. Agregar campo `stock` para control de inventario
3. Implementar búsqueda y filtros avanzados
4. Crear tabla `product_images` para galería de imágenes
5. Implementar wishlist/favoritos
6. Sistema de reviews y ratings

---

## 3️⃣ SERVICIO DE ÓRDENES

**Directorio:** `NNProtect_new_website/order_service/`
**Estado:** ✅ 80% IMPLEMENTADO

### Archivos Clave
- `orders.py` - Lista de órdenes del usuario
- `order_details.py` - Detalles de una orden
- `shipment.py` - Métodos de envío

### Funcionalidades Implementadas
✅ **Creación de Órdenes**
- Orden creada desde carrito de compras
- Estados de orden definidos (Enum OrderStatus):
  - DRAFT (en carrito, no enviada)
  - PENDING_PAYMENT (enviada, esperando pago)
  - PAYMENT_CONFIRMED (pago confirmado - TRIGGER COMISIONES)
  - PROCESSING (en preparación)
  - SHIPPED (enviada al cliente)
  - DELIVERED (entregada)
  - CANCELLED / REFUNDED

✅ **Cálculos de Orden**
- Subtotal, envío, impuestos, descuentos
- `total_pv`: Puntos de volumen totales
- `total_vn`: Valor neto para comisiones
- Moneda según país del usuario

✅ **Timestamps Críticos (UTC)**
- `created_at`: Creación de orden
- `submitted_at`: Cuando se envía la orden
- `payment_confirmed_at`: ⚠️ **CRÍTICO** - Determina período y trigger de comisiones
- `shipped_at` / `delivered_at`: Logística

✅ **Asignación de Período**
- `period_id`: Se asigna cuando `payment_confirmed_at` se establece
- ⚠️ **IMPORTANTE**: El período se determina por `payment_confirmed_at`, NO por `created_at`

### Modelos de Base de Datos
Directorio: `database/`
- `orders.py` - Órdenes con campos:
  - `member_id` (comprador)
  - `country`, `currency`
  - `subtotal`, `shipping_cost`, `tax`, `discount`, `total`
  - `total_pv`, `total_vn`
  - `status` (OrderStatus enum)
  - `payment_confirmed_at` (CRÍTICO para período)
  - `period_id` (FK a periods)
  - `payment_method`, `payment_reference`
  - `shipping_address_id`

- `order_items.py` - Items de órdenes:
  - `order_id`, `product_id`
  - `quantity`, `price`
  - `pv`, `vn` (valores congelados al momento de la compra)

### Estado de Implementación
| Feature | Estado | Notas |
|---------|--------|-------|
| Creación de Órdenes | ✅ 90% | Desde carrito funcional |
| Estados de Orden | ✅ 100% | Enum definido |
| Cálculo de Totales | ✅ 100% | PV/VN correcto |
| Timestamps UTC | ✅ 100% | payment_confirmed_at crítico |
| Asignación de Período | ✅ 100% | Por payment_confirmed_at |
| Tracking de Envío | ⚠️ 50% | Modelo creado, lógica parcial |
| Cancelación de Órdenes | ⚠️ 30% | Solo cambio de status |
| Reembolsos | ❌ 0% | No implementado |

### ⚠️ PROBLEMAS IDENTIFICADOS
1. **NO existe tabla `transactions`**:
   - Según DB_MLM_README, debería haber tabla separada
   - Actualmente todo está en `orders`
   - ⚠️ **DECISIÓN DE ARQUITECTURA**: Mantener solo `orders` es VÁLIDO si:
     - Se congela PV/VN en `order_items` (✅ Ya implementado)
     - Se usa `payment_confirmed_at` para período (✅ Ya implementado)

2. **Falta confirmación de pago automatizada**:
   - Actualmente es manual (cambio de status)
   - Necesita webhook de Stripe

3. **No hay reversión de comisiones en reembolsos**: Lógica faltante

### Próximos Pasos para el Equipo
1. Implementar webhook de Stripe para confirmar pago automáticamente
2. Implementar lógica de cancelación completa (reversión de PV/comisiones)
3. Sistema de reembolsos con reversión de comisiones
4. Tracking de envío en tiempo real
5. Notificaciones de cambio de status de orden
6. Panel admin para gestión de órdenes

---

## 4️⃣ SERVICIO DE PAGOS

**Directorio:** `NNProtect_new_website/payment_service/`
**Estado:** ⚠️ 30% IMPLEMENTADO (SOLO UI)

### Archivos Clave
- `payment.py` - UI de métodos de pago (solo frontend)

### Funcionalidades Implementadas
✅ **UI de Métodos de Pago (Solo Frontend)**
- Diseño responsive de opciones de pago:
  - Saldo en billetera (diseñado pero no funcional)
  - Tarjeta débito/crédito (placeholder)
  - OXXO (placeholder)
  - Pago en efectivo (placeholder)
  - Criptomonedas (placeholder)

### Estado de Implementación
| Feature | Estado | Notas |
|---------|--------|-------|
| UI de Métodos de Pago | ✅ 100% | Solo diseño |
| Integración Stripe | ❌ 0% | No implementado |
| Pago con Wallet | ❌ 0% | No implementado |
| Webhooks de Pago | ❌ 0% | No implementado |
| OXXO Integration | ❌ 0% | No implementado |
| Confirmación Automática | ❌ 0% | No implementado |

### ⚠️ ESTADO CRÍTICO
**Este servicio está prácticamente VACÍO. Solo existe la interfaz visual.**

### Próximos Pasos para el Equipo (PRIORIDAD ALTA)
1. ⚠️ **URGENTE**: Implementar integración Stripe multi-país
   - México: OXXO, SPEI, tarjetas
   - USA: ACH, tarjetas
   - Colombia: PSE, tarjetas
   - República Dominicana: tarjetas

2. Crear `PaymentService` con métodos:
   - `create_payment_intent(order_id, amount, currency, country)`
   - `process_payment_webhook(event)` - Handler de webhooks Stripe
   - `handle_payment_success(payment_intent_id)` - Confirmar orden
   - `handle_payment_failure(payment_intent_id, reason)`
   - `process_refund(order_id, amount, reason)`

3. Implementar pago con wallet:
   - Validar balance suficiente
   - Descontar de wallet al pagar
   - Crear transacción en `wallet_transactions`

4. Configurar webhooks de Stripe:
   - `payment_intent.succeeded` → Confirmar orden + trigger comisiones
   - `payment_intent.payment_failed` → Notificar usuario
   - `charge.refunded` → Reversar comisiones

5. Tabla de logs de pagos para auditoría

---

## 5️⃣ SERVICIO MULTINIVEL (MLM)

**Directorio:** `NNProtect_new_website.modules.network.backend/`
**Estado:** ✅ 85% IMPLEMENTADO (Core funcional, bonos avanzados faltantes)

### Archivos Clave Implementados
- `mlm_user_manager.py` - Manager principal de usuarios MLM ✅
- `genealogy_service.py` - Gestión de árbol genealógico ✅
- `rank_service.py` - Sistema automático de rangos ✅
- `commission_service.py` - Cálculo de comisiones ✅
- `period_service.py` - Gestión de períodos mensuales ✅
- `pv_update_service.py` - Actualización de cache PV/PVG ✅
- `pv_reset_service.py` - Reset mensual de PV ✅
- `exchange_service.py` - Conversión de monedas ✅
- `scheduler_service.py` - Tareas automáticas programadas ✅
- `network_reports.py` - Reportes de red en tiempo real ✅
- `income_reports.py` - Reportes de ingresos ✅
- `wallet_service.py` - Servicio de billetera ✅
- `cashback_service.py` - Servicio de cashback ⚠️
- `loyalty_service.py` - Servicio de lealtad ⚠️
- `travel_points_service.py` - Puntos NN Travel ⚠️

### 5.1 GENEALOGÍA MLM

**Estado:** ✅ 100% IMPLEMENTADO Y OPTIMIZADO

#### Patrón: Path Enumeration
- Tabla `user_tree_paths` almacena TODAS las relaciones ancestro-descendiente pre-calculadas
- Formato: `(ancestor_id, descendant_id, depth)` donde depth=0 es auto-referencia
- Permite queries O(1) sin recursión
- Crítico para performance con 50k+ usuarios

#### Métodos Implementados (GenealogyService)
✅ `add_member_to_tree(session, new_member_id, sponsor_id)`
- Inserta auto-referencia (depth=0)
- Inserta paths a TODOS los ancestros
- Se ejecuta automáticamente al registrar usuario

✅ `get_descendants(session, member_id)` - Obtiene todos los descendientes
✅ `get_ancestors(session, member_id)` - Obtiene todos los ancestros

#### Optimizaciones Aplicadas (Octubre 2025)
✅ Query de descendientes en SINGLE JOIN (antes eran N+1 queries)
✅ Eliminación de BFS recursivo para calcular niveles
✅ Usa `tree_path.depth` directamente
✅ Cache de datos de sponsors en single query
✅ **FIX CRÍTICO**: `Users.member_id` (no `Users.id`) para sponsor lookup

#### Modelos de Base de Datos
- `usertreepaths.py` - UserTreePath con composite PK:
  - `ancestor_id` (member_id del ancestro)
  - `descendant_id` (member_id del descendiente)
  - `depth` (0=self, 1=hijo, 2=nieto, 3=bisnieto...)

#### Índices Críticos
```sql
CREATE INDEX idx_tree_path_ancestor_depth ON user_tree_paths(ancestor_id, depth);
CREATE INDEX idx_tree_path_descendant_depth ON user_tree_paths(descendant_id, depth);
```

### 5.2 SISTEMA DE RANGOS

**Estado:** ✅ 100% IMPLEMENTADO Y FUNCIONAL

#### 9 Rangos Definidos (tabla `ranks`)
1. Sin rango (0 PVG requerido)
2. Visionario (1,465 PVG)
3. Emprendedor (21,000 PVG)
4. Creativo (58,000 PVG)
5. Innovador (120,000 PVG)
6. Embajador Transformador (300,000 PVG)
7. Embajador Inspirador (650,000 PVG)
8. Embajador Consciente (1,300,000 PVG)
9. Embajador Solidario (2,900,000 PVG)

#### Reglas de Rangos
- **Requisito mínimo**: 1,465 PV personal + PVG específico
- **Los rangos NUNCA retroceden**: Una vez alcanzado, se mantiene de por vida
- **Promoción automática**: Al cumplir requisitos de PV+PVG
- **Trigger de Achievement Bonus**: Al subir de rango por primera vez

#### Métodos Implementados (RankService)
✅ `assign_initial_rank(session, member_id)` - Asigna "Sin rango" al registrarse
✅ `get_user_current_rank(session, member_id)` - Rango actual (último en historial)
✅ `get_user_highest_rank(session, member_id)` - Rango máximo de por vida
✅ `get_user_current_month_rank(session, member_id)` - Rango del período actual
✅ `calculate_rank(session, member_id, period_id)` - Determina rango por PV+PVG
✅ `promote_user_rank(session, member_id, new_rank_id)` - Promociona a nuevo rango
✅ `check_and_update_rank(session, member_id)` - Verifica y promueve automáticamente

#### Correcciones Críticas (Octubre 2025)
✅ Uso de `datetime.now(timezone.utc)` en lugar de `get_mexico_now()` para comparación de fechas
✅ Agregado `traceback.print_exc()` para debugging
✅ Retorno de nombres de rangos (strings) en lugar de IDs

#### Modelos de Base de Datos
- `ranks.py` - Ranks con campos:
  - `name` (nombre del rango)
  - `pvg_required` (PVG requerido para alcanzar)
  - `achievement_bonus_usd` (bono one-time al alcanzar)

- `user_rank_history.py` - Historial de rangos:
  - `member_id`, `rank_id`
  - `achieved_on` (timestamp UTC)
  - `period_id` (período en que se alcanzó)

### 5.3 SISTEMA DE PUNTOS (PV/PVG/VN)

**Estado:** ✅ 100% IMPLEMENTADO

#### Definiciones
- **PV (Personal Volume)**: Puntos de volumen personal, usados SOLO para calificar a rangos
- **PVG (Group Volume)**: Suma de PV del usuario + TODOS sus descendientes, determina el rango real
- **VN (Business Value)**: Valor neto monetario por país, usado SOLO para cálculo de comisiones

#### Cache en Tabla Users
- `pv_cache`: PV acumulado del mes actual
- `pvg_cache`: PVG acumulado del mes actual
- Actualizado automáticamente al confirmar pago de orden

#### Reset Mensual Automático
- Job programado: Día 1 de cada mes a las 00:00 (México Central)
- Ejecuta: `UPDATE users SET pv_cache = 0, pvg_cache = 0`
- Service: `PVResetService.reset_all_users_pv()`

#### Métodos Implementados
✅ `RankService.get_pv(session, member_id, period_id)` - Calcula PV de órdenes confirmadas
✅ `RankService.get_pvg(session, member_id, period_id)` - PV personal + PV de descendientes
✅ `PVUpdateService.update_user_pv_cache(session, member_id)` - Actualiza cache
✅ `PVUpdateService.update_all_users_pv()` - Actualización masiva (batch)

#### Reglas Críticas
- PV solo se genera con status `PAYMENT_CONFIRMED`
- PVG incluye PV del usuario + toda su red descendente
- Reset automático el primer día del mes (scheduler)
- `payment_confirmed_at` determina el período (NO `created_at`)

### 5.4 SISTEMA DE COMISIONES

**Estado:** ✅ 60% IMPLEMENTADO (5 de 9 bonos implementados)

#### Bonos Implementados ✅

**1. Bono Rápido (Fast Start Bonus)** ✅ 100%
- Paga al confirmar compra de KIT (productos is_kit=true)
- Nivel 1: 30% del PV del kit
- Nivel 2: 10% del PV del kit
- Nivel 3: 5% del PV del kit
- Instantáneo, NO mensual
- Service: `CommissionService.process_fast_start_bonus()`

**2. Bono Uninivel (Unilevel Bonus)** ✅ 100%
- Mensual (día 31 del mes)
- Hasta 10 niveles de profundidad
- Porcentajes por rango definidos (5-10% según nivel y rango)
- Basado en VN de productos (NO kits)
- Service: `CommissionService.process_unilevel_bonus()`

**3. Bono por Alcance (Achievement Bonus)** ✅ 100%
- One-time al alcanzar rango por primera vez
- Montos por rango (en MXN, USD, COP):
  - Emprendedor: $1,500 MXN / $85 USD / $330k COP
  - Creativo: $3,000 MXN / $165 USD / $666k COP
  - ...hasta Embajador Solidario: $40,000 MXN
- Service: `CommissionService.process_achievement_bonus()`

**4. Bono Matching** ✅ 100%
- Solo para rangos Embajador (Transformador+)
- Porcentajes de matching sobre uninivel del equipo:
  - Embajador Transformador: 30% (1 nivel)
  - Embajador Inspirador: 30%, 20% (2 niveles)
  - Embajador Consciente: 30%, 20%, 10% (3 niveles)
  - Embajador Solidario: 30%, 20%, 10%, 5% (4 niveles)
- Service: `CommissionService.process_matching_bonus()`

**5. Bono Directo (Direct Bonus)** ✅ 100%
- 25% del VN en ventas directas (nivel 1)
- Service: `CommissionService.process_direct_bonus()`

#### Bonos NO Implementados ❌ (Pendientes)

**6. Bono de Liderazgo (Leadership Bonus)** ❌ 0%
- Para rangos Embajador Transformador+
- Porcentaje sobre VN total del grupo
- 2-5% según rango
- ⚠️ Falta implementación completa

**7. Bono de Automóvil (Car Bonus)** ❌ 0%
- Enganche: $50,000 MXN (one-time)
- Mensualidad: $5,000 MXN/mes mientras mantenga rango
- Requisito: Embajador Transformador+ por 2 meses consecutivos
- ⚠️ Falta tabla `car_bonus_status` y lógica completa

**8. Bono Cashback** ⚠️ 30%
- 79% descuento en siguiente compra
- Requisito: 2,930 PV en un mismo mes
- ✅ Tabla `cashback` creada
- ⚠️ Servicio parcial en `cashback_service.py`
- ❌ Lógica de activación y redención incompleta

**9. Bono de Lealtad (Loyalty Bonus)** ⚠️ 30%
- Regalo físico por comprar entre día 1-7 durante 4 meses consecutivos
- ✅ Tabla `loyalty_points` creada
- ⚠️ Servicio parcial en `loyalty_service.py`
- ❌ Tracking de streak y entrega de gifts faltante

#### Modelos de Base de Datos
- `comissions.py` - Commissions con campos:
  - `member_id` (receptor)
  - `bonus_type` (ENUM: bono_rapido, bono_uninivel, etc.)
  - `source_member_id`, `source_order_id` (origen)
  - `period_id` (período mensual)
  - `level_depth` (para uninivel: 1-10)
  - `amount_vn` (monto en VN original)
  - `currency_origin`, `currency_destination`
  - `amount_converted`, `exchange_rate`
  - `status` (PENDING, PAID, CANCELLED)
  - `calculated_at`, `paid_at` (timestamps UTC)

#### Conversión de Monedas
✅ `ExchangeService` implementado
- Tabla `exchange_rates` con tasas fijas por la empresa (NO market rates)
- Conversión automática a moneda del receptor
- Exchange rate guardado en cada comisión para auditoría

### 5.5 GESTIÓN DE PERÍODOS

**Estado:** ✅ 100% IMPLEMENTADO

#### Períodos Mensuales
- Tabla `periods` con:
  - `name` (ej: "Octubre 2025")
  - `starts_on`, `ends_on` (timestamps UTC)
  - `closed_at` (NULL si activo, timestamp si cerrado)

#### Lógica de Períodos
- Período actual: `WHERE closed_at IS NULL`
- Cierre automático: Último día del mes a las 23:59:59 (México)
- Creación automática: Día 1 del mes a las 00:00 (México)
- Service: `PeriodService.get_current_period()`

#### Jobs Programados (Scheduler)
✅ `SchedulerService.start_scheduler()` - Inicializa en app startup
- **Reset de PV/PVG**: Día 1 @ 00:00 México
- **Cierre de período**: Último día @ 23:59 México
- Usa APScheduler con timezone México Central

### 5.6 WALLET (BILLETERA DIGITAL)

**Estado:** ✅ 90% IMPLEMENTADO

#### Funcionalidades
✅ Tabla `wallets` con balance por usuario
✅ Tabla `wallettransactions` para historial completo
✅ Tabla `walletwithdrawals` para solicitudes de retiro
✅ `WalletService` con métodos:
  - `get_wallet(member_id)` - Obtener wallet
  - `credit_commission(wallet_id, commission_id, amount)` - Agregar comisión
  - `debit_withdrawal(wallet_id, amount, withdrawal_id)` - Descontar retiro
  - `get_balance(wallet_id)` - Balance actual
  - `get_transaction_history()` - Historial paginado

#### Reglas de Negocio
- Balance NUNCA puede ser negativo (CHECK CONSTRAINT)
- Moneda según país del usuario
- Estados de wallet: ACTIVE, SUSPENDED, CLOSED
- Transacciones inmutables (nunca se modifican, solo se crean)
- UUID para idempotencia (evita duplicados)

#### Modelos de Base de Datos
- `wallet.py` - 3 tablas:
  - `wallets` - Balance por usuario
  - `wallettransactions` - Historial de movimientos
  - `walletwithdrawals` - Solicitudes de retiro

#### Tipos de Transacciones
- **Créditos**: commission_deposit, transfer_in, refund, adjustment_credit
- **Débitos**: order_payment, transfer_out, withdrawal_request, adjustment_debit

### 5.7 REPORTES DE RED

**Estado:** ✅ 100% IMPLEMENTADO

#### Páginas de Reportes
✅ `network_reports.py` - Reportes de red completos
- Detalles personales del usuario
- Datos del patrocinador
- Reporte de volumen (PV, PVG)
- Inscripciones del día y del mes
- Tabla de descendientes con niveles

✅ `income_reports.py` - Reportes de ingresos
- Comisiones por tipo
- Historial de pagos
- Gráficas de ingresos

✅ `network.py` - Visualización de red MLM (árbol)

#### Estado de Implementación (Reportes)
| Feature | Estado | Notas |
|---------|--------|-------|
| Reporte de Volumen | ✅ 100% | PV/PVG en tiempo real |
| Descendientes con Niveles | ✅ 100% | Query optimizada |
| Inscripciones del Día/Mes | ✅ 100% | Funcional |
| Árbol Genealógico Visual | ⚠️ 70% | UI básica, falta interactividad |
| Reportes de Comisiones | ✅ 90% | Historial completo |
| Exportar a PDF/Excel | ❌ 0% | No implementado |

### 5.8 ADMIN APP

**Directorio:** `NNProtect_new_website/Admin_app/`
**Estado:** ⚠️ 40% IMPLEMENTADO (UI básica, lógica faltante)

#### Archivos
- `admin_page.py` - Página principal del admin
- `admin_state.py` - Estado del admin
- `components.py` - Componentes UI
- `theme.py` - Tema del admin panel

#### Funcionalidades Actuales
⚠️ Solo UI básica, sin lógica de backend
❌ No hay sistema de roles/permisos funcional
❌ No hay gestión de usuarios
❌ No hay aprobación de comisiones/retiros
❌ No hay configuración de productos/tasas

---

## 📊 RESUMEN DEL ESTADO ACTUAL

### Servicios por Estado General

| Servicio | Estado Global | %  Completo | Prioridad |
|----------|---------------|-------------|-----------|
| 1. Autenticación | ✅ FUNCIONAL | 90% | BAJA |
| 2. Tienda | ✅ FUNCIONAL | 90% | MEDIA |
| 3. Órdenes | ✅ FUNCIONAL | 80% | MEDIA |
| 4. Pagos | ❌ CRÍTICO | 30% | **ALTA** |
| 5. MLM | ✅ FUNCIONAL | 85% | MEDIA |

### ✅ Lo que FUNCIONA y está LISTO
1. Login/Registro con JWT
2. Catálogo de productos con 24 productos reales
3. Carrito de compras funcional
4. Creación de órdenes con cálculo de PV/VN
5. Genealogía con Path Enumeration optimizada
6. Sistema automático de rangos (9 rangos)
7. Cache de PV/PVG con reset mensual
8. 5 tipos de comisiones (Fast, Uninivel, Achievement, Matching, Direct)
9. Wallet digital con transacciones
10. Reportes de red en tiempo real
11. Jobs programados (reset PV, cierre períodos)

### ❌ Lo que está INCOMPLETO o FALTA
1. **CRÍTICO**: Integración de pagos Stripe (solo UI)
2. **CRÍTICO**: Distinción Kit vs Producto en BD
3. **CRÍTICO**: Admin Panel funcional
4. 4 bonos faltantes (Liderazgo, Automóvil, Cashback completo, Lealtad completa)
5. Sistema de roles y permisos
6. Webhooks de pago automatizados
7. Confirmación de pago automática
8. Reversión de comisiones en cancelaciones
9. Exportación de reportes a PDF/Excel
10. Sistema de notificaciones push
11. Búsqueda avanzada de productos
12. Control de inventario (stock)

---

## 🔧 COMANDOS CLAVE PARA EL EQUIPO

### Desarrollo
```bash
# Activar entorno virtual
source nnprotect_backoffice/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
reflex run

# Ejecutar en producción
reflex run --env prod

# Migraciones de BD
alembic upgrade head

# Crear nueva migración
alembic revision --autogenerate -m "descripción"
```

### Testing
```bash
# Test de red genealógica
python testers/test_network_descendants.py

# Test de sistema de rangos
python testers/test_automatic_rank_system.py

# Verificar estructura de árbol
python testers/verify_user_tree.py

# Crear orden de prueba
python testers/create_test_order.py
```

### Operaciones de BD
```bash
# Ver período actual
python -c "from mlm_service.period_service import PeriodService; print(PeriodService.get_current_period())"

# Actualizar PV/PVG de un usuario
python -c "from mlm_service.pv_update_service import PVUpdateService; PVUpdateService.update_user_pv_cache(member_id=1)"

# Verificar rango actual
python -c "from mlm_service.rank_service import RankService; import reflex as rx; with rx.session() as s: print(RankService.get_user_current_rank(s, 1))"
```

---

## ⚠️ PROBLEMAS CRÍTICOS CONOCIDOS

### 1. NO existe distinción Kit vs Producto
**Impacto:** CRÍTICO para comisiones
**Problema:**
- Los kits deben generar PV pero NO VN
- Los productos generan PV y VN
- Actualmente todos generan ambos (incorrecto)

**Solución:**
```sql
ALTER TABLE products ADD COLUMN is_kit BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN generates_vn BOOLEAN DEFAULT TRUE;

-- Marcar kits existentes
UPDATE products SET is_kit = TRUE, generates_vn = FALSE WHERE presentation = 'kit';
```

### 2. Timestamps UTC vs México
**Impacto:** MEDIO (ya corregido en mayoría del código)
**Regla:**
- Almacenar SIEMPRE en UTC
- Usar `datetime.now(timezone.utc)` para comparaciones
- Convertir a México solo para DISPLAY
- NUNCA hardcodear offsets (rompe con DST)

### 3. payment_confirmed_at determina período
**Impacto:** CRÍTICO
**Regla:**
- El `payment_confirmed_at` (NO `created_at`) determina el período de la orden
- Esto afecta: PV/PVG del mes, comisiones generadas, reportes

### 4. Servicio de Pagos vacío
**Impacto:** BLOQUEANTE PARA PRODUCCIÓN
**Problema:** Solo existe la UI, no hay integración real con Stripe

---

## 📝 CONVENCIONES Y PATRONES

### Principios Aplicados
- **KISS** (Keep It Simple, Stupid): Soluciones simples y directas
- **DRY** (Don't Repeat Yourself): Servicios reutilizables
- **YAGNI** (You Aren't Gonna Need It): No especular
- **POO**: Diseño orientado a objetos con servicios

### Patrón de Servicios POO
```python
class ServiceName:
    """Docstring explicando el servicio."""

    @classmethod
    def method_name(cls, session, param1, param2):
        """Docstring del método."""
        try:
            # Lógica de negocio
            pass
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return default_value
```

### Timezone Pattern
```python
# ✅ CORRECTO
from datetime import datetime, timezone
now_utc = datetime.now(timezone.utc)

# ❌ INCORRECTO
from utils.timezone_mx import get_mexico_now
now_mx = get_mexico_now()  # Solo para display, NO para lógica
```

### State Pattern (Reflex)
```python
# Páginas deben refrescar datos
on_mount=[AuthState.load_user_from_token, OtherState.load_data]

# Acceso a datos en componentes
AuthState.profile_data.get("pv_cache")
AuthState.profile_data.get("current_month_rank")
```

---

## 🎯 PRIORIDADES PARA EL NUEVO EQUIPO

### FASE 1: PAGOS (Semanas 3-6) - PRIORIDAD ALTA
1. Pago con wallet
2. Implementar `PaymentService` completo
3. Testing E2E de flujo de pago

### FASE 2: BONOS FALTANTES (Semanas 7-10)
1. Bono de Liderazgo
2. Bono de Automóvil
3. Completar Bono Cashback
4. Completar Bono de Lealtad
5. Testing de pago de comisiones funcional al 100%

### FASE 3: ADMIN PANEL (Semanas 11-14)
1. Sistema de roles y permisos
2. Gestión de usuarios
3. Aprobación de comisiones/retiros
4. Configuración de productos y tasas
5. Dashboard ejecutivo

### FASE 4: OPTIMIZACIONES (Semanas 15-18)
1. Notificaciones push
2. Exportar reportes a PDF/Excel
3. Búsqueda avanzada de productos
4. Performance optimization para 50k usuarios

---

## 📚 DOCUMENTACIÓN ADICIONAL

- **README.md**: Documentación completa en español
- **MLM_SCHEME_README.md**: Plan de compensación MLM detallado
- **DB_MLM_README.md**: Diseño de base de datos y decisiones arquitectónicas
- **COMPLIANCE_REPORT.md**: Reporte de compliance financiero
- **WALLET_POINTS_IMPLEMENTATION_SUMMARY.md**: Implementación de wallet y puntos

---

## 🔐 CONFIGURACIÓN DE ENTORNO

### Variables de Entorno Requeridas (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# JWT
JWT_SECRET_KEY=your_secret_key_here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here

# Environment
ENVIRONMENT=DESARROLLO  # o PRODUCCION
BASE_URL=http://localhost:3000  # o dominio en producción
```

---

## 📞 CONTACTO Y SOPORTE

Para consultas sobre el estado actual del proyecto o decisiones arquitectónicas tomadas, consultar la documentación completa en:
- README.md
- MLM_SCHEME_README.md
- DB_MLM_README.md

**Última Actualización:** Octubre 1, 2025
**Versión del Documento:** 1.0
**Estado del Proyecto:** Entregado para continuación por nuevo equipo
