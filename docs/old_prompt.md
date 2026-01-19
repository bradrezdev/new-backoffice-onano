# Prompt para IA: Implementación Backend MLM NN Protect

## 🎯 Objetivo Principal
Implementar el backend funcional completo para el sistema MLM NN Protect, conectando las tablas de base de datos recién creadas con la lógica de negocio documentada en los READMEs del proyecto.

## ⚡ Decisiones Arquitectónicas Clave (CONFIRMADAS)

### 1. Sistema de Órdenes
✅ **Transactions será REEMPLAZADA** por `Orders` + `OrderItems`
- Eliminar toda referencia a tabla `Transactions`
- Migrar lógica existente a nuevo modelo de órdenes

### 2. Inserción en UserTreePath
✅ **Al confirmar registro** (sin validaciones previas)
- NO requiere validación de email
- NO requiere pago previo
- Transacción atómica: registro + genealogía

### 3. Cálculo de PVG
✅ **Tiempo real SIEMPRE** (no pre-calcular)
- Query dinámico cada vez que se necesita
- Priorizar precisión sobre velocidad
- Optimizar con índices apropiados

### 4. Confirmación de Pagos
✅ **Webhook primario + Fallback manual**
- Automático: Webhook desde Stripe/PayPal
- Manual: Admin puede confirmar si webhook falla
- Retry mechanism para webhooks perdidos

---

## 📋 Contexto del Proyecto

### Stack Tecnológico
- **Backend**: Python + SQLModel + Supabase (PostgreSQL)
- **Frontend**: Reflex (framework Python para web)
- **ORM**: SQLModel
- **Base de datos**: PostgreSQL vía Supabase

### Estado Actual
- ✅ Tablas de base de datos optimizadas (database/)
- ✅ Documentación completa del plan de compensación (READMEs)
- ✅ Sistema de autenticación con Supabase
- ✅ `reflex db init` funcionando correctamente
- ⚠️ Tabla `Transactions` existe pero será ELIMINADA
- ❌ Tablas `Orders` + `OrderItems` NO existen
- ❌ Lógica de negocio NO implementada
- ❌ Cálculos de comisiones NO implementados
- ❌ Jobs programados NO configurados

### Archivos de Referencia Críticos
1. `DB_MLM_README.md` - Arquitectura completa de base de datos
2. `MLM_SCHEME_README.md` - Reglas de negocio y fórmulas
3. `database/` - Definiciones de tablas SQLModel existentes
4. `utils/timezone_mx.py` - Utilidad de timezone (si existe)

---

## 🎯 Tareas a Implementar

### Fase 1: Crear Tabla Orders (Órdenes)
**Prioridad**: CRÍTICA

Crear modelo `Orders` que maneje el flujo completo de pedidos mensuales:

```python
# models/orders.py
from sqlmodel import Field, Relationship
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    DRAFT = "draft"              # Orden en carrito (no enviada)
    PENDING_PAYMENT = "pending_payment"  # Enviada, esperando pago
    PAYMENT_CONFIRMED = "payment_confirmed"  # Pago confirmado
    PROCESSING = "processing"    # En proceso de preparación
    SHIPPED = "shipped"          # Enviada al cliente
    DELIVERED = "delivered"      # Entregada
    CANCELLED = "cancelled"      # Cancelada
    REFUNDED = "refunded"        # Reembolsada

class Orders(rx.Model, table=True):
    """
    Órdenes de compra mensuales.
    Una orden puede contener múltiples productos (items).
    """
    id: int | None = Field(default=None, primary_key=True, index=True)
    
    # Comprador
    member_id: int = Field(foreign_key="users.member_id", index=True)
    
    # País y moneda de la orden
    country: str = Field(max_length=50, index=True)
    currency: str = Field(max_length=10)  # MXN, USD, COP
    
    # Totales de la orden
    subtotal: float = Field(default=0.0)
    shipping_cost: float = Field(default=0.0)
    tax: float = Field(default=0.0)
    discount: float = Field(default=0.0)  # Cashback u otros descuentos
    total: float = Field(default=0.0)
    
    # Puntos totales generados por esta orden
    total_pv: int = Field(default=0)
    total_vn: float = Field(default=0.0)
    
    # Estado de la orden
    status: str = Field(default=OrderStatus.DRAFT.value, index=True)
    
    # Dirección de envío
    shipping_address_id: int = Field(foreign_key="addresses.id")
    
    # Timestamps críticos
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    submitted_at: datetime | None = Field(default=None)  # Cuando envía la orden
    payment_confirmed_at: datetime | None = Field(default=None, index=True)  # Cuando paga
    shipped_at: datetime | None = Field(default=None)
    delivered_at: datetime | None = Field(default=None)
    
    # Período al que pertenece (basado en payment_confirmed_at)
    period_id: int | None = Field(default=None, foreign_key="periods.id", index=True)
    
    # Información de pago
    payment_method: str | None = Field(default=None, max_length=50)
    payment_reference: str | None = Field(default=None, unique=True)
    
    # Notas
    customer_notes: str | None = Field(default=None, max_length=500)
    admin_notes: str | None = Field(default=None, max_length=500)

class OrderItems(rx.Model, table=True):
    """
    Items individuales dentro de una orden.
    Cada línea representa un producto y su cantidad.
    """
    id: int | None = Field(default=None, primary_key=True, index=True)
    
    order_id: int = Field(foreign_key="orders.id", index=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    
    quantity: int = Field(default=1)
    
    # Valores congelados al momento de agregar al carrito
    unit_price: float = Field(default=0.0)
    unit_pv: int = Field(default=0)
    unit_vn: float = Field(default=0.0)
    
    # Totales de esta línea
    line_total: float = Field(default=0.0)  # quantity * unit_price
    line_pv: int = Field(default=0)         # quantity * unit_pv
    line_vn: float = Field(default=0.0)     # quantity * unit_vn
```

**✅ DECISIÓN CONFIRMADA**:
La tabla `Transactions` será **REEMPLAZADA** completamente por `Orders` + `OrderItems`.
- Toda lógica existente que use `Transactions` debe migrarse a `Orders`
- Los cálculos de comisiones se basarán en `Orders` con `status='PAYMENT_CONFIRMED'`
- No mantener ambas tablas para evitar redundancia

---

### Fase 2: Implementar Triggers de Comisiones

**Archivo**: `services/commission_calculator.py`

```python
class CommissionCalculator:
    """
    Servicio centralizado para cálculo de comisiones.
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    def on_payment_confirmed(self, order_id: int):
        """
        Trigger cuando se confirma el pago de una orden.
        Calcula comisiones instantáneas (Bono Rápido si es kit).
        """
        pass
    
    def calculate_fast_bonus(self, order_id: int):
        """
        Calcula Bono Rápido si la orden contiene kit de inicio.
        Se ejecuta INMEDIATAMENTE al confirmar pago.
        """
        pass
    
    def calculate_monthly_bonuses(self, period_id: int):
        """
        Calcula todos los bonos mensuales (Uninivel, Matching, etc).
        Se ejecuta el día 31 a las 23:59:59.
        """
        pass
    
    def calculate_unilevel_bonus(self, member_id: int, period_id: int):
        """
        Calcula Bono Uninivel para un miembro en un período.
        """
        pass
    
    def calculate_matching_bonus(self, member_id: int, period_id: int):
        """
        Calcula Matching Bonus para Embajadores.
        """
        pass
```

---

### Fase 3: Implementar Gestión de Genealogía

**Archivo**: `services/genealogy_service.py`

```python
class GenealogyService:
    """
    Servicio para manejar la estructura de red (UserTreePath).
    """
    
    def add_member_to_tree(self, new_member_id: int, sponsor_id: int):
        """
        Agrega un nuevo miembro al árbol genealógico.
        Crea TODOS los registros necesarios en UserTreePath.
        """
        pass
    
    def get_upline(self, member_id: int, depth: int = None):
        """
        Obtiene los patrocinadores ascendentes de un miembro.
        """
        pass
    
    def get_downline(self, member_id: int, depth: int = None):
        """
        Obtiene todos los descendientes de un miembro.
        """
        pass
    
    def get_level_members(self, member_id: int, level: int):
        """
        Obtiene todos los miembros de un nivel específico.
        """
        pass
```

---

### Fase 4: Implementar Sistema de Rangos

**Archivo**: `services/rank_service.py`

```python
class RankService:
    """
    Servicio para calcular y actualizar rangos de usuarios.
    """
    
    def calculate_rank(self, member_id: int):
        """
        Calcula el rango de un miembro basándose en PV y VG.
        """
        pass
    
    def update_rank_if_changed(self, member_id: int):
        """
        Verifica si el rango cambió y actualiza historial.
        Dispara Bono por Alcance si es nuevo rango.
        """
        pass
    
    def get_pv(self, member_id: int, period_id: int = None):
        """
        Obtiene el PV personal de un miembro.
        """
        pass
    
    def get_vg(self, member_id: int, period_id: int = None):
        """
        Obtiene el VG (volumen grupal) de un miembro.
        """
        pass
```

---

### Fase 5: Implementar Jobs Programados

**Archivo**: `jobs/monthly_closure.py`

```python
from apscheduler.schedulers.background import BackgroundScheduler

def monthly_closure_job():
    """
    Job que se ejecuta el día 31 de cada mes a las 23:59:59.
    Calcula todas las comisiones mensuales.
    """
    pass

def setup_scheduled_jobs():
    """
    Configura todos los jobs programados del sistema.
    """
    scheduler = BackgroundScheduler()
    
    # Job de cierre mensual
    scheduler.add_job(
        monthly_closure_job,
        'cron',
        day='last',
        hour=23,
        minute=59,
        second=59
    )
    
    scheduler.start()
```

---

## 🔥 HOTSPOTS CRÍTICOS DEL PROYECTO

### Hotspot 1: Relación Orders ↔ Transactions
**Ubicación**: `models/orders.py`, `models/transactions.py`  
**Problema**: Duplicación de propósito entre ambas tablas  
**Decisión requerida**: ¿Migrar todo a Orders o mantener ambas?  
**Impacto**: Alto - Afecta TODOS los cálculos de comisiones  
**Recomendación**: Consolidar en Orders + OrderItems

### Hotspot 2: UserTreePath - Inserción al Registrar Usuario
**Ubicación**: `services/genealogy_service.py`, registro de usuarios  
**Problema**: ¿Cuándo se crea el árbol genealógico?  
**Crítico**: Debe crearse INMEDIATAMENTE al confirmar registro  
**Riesgo**: Si falla, el usuario queda "huérfano" sin sponsor  
**Solución**: Transaction atómica: registro + genealogía

### Hotspot 3: Cálculo de VG (Volumen Grupal)
**Ubicación**: `services/rank_service.py`  
**Problema**: Query puede ser muy lenta con 50k usuarios  
**Crítico**: Se usa para determinar rangos  
**Riesgo**: Timeout en queries con redes grandes  
**Solución**: Considerar materializar VG en campo denormalizado

### Hotspot 4: Conversión de Monedas en Comisiones
**Ubicación**: `services/commission_calculator.py`  
**Problema**: ¿Cómo obtener la tasa de cambio vigente?  
**Crítico**: Afecta TODOS los cálculos de comisiones internacionales  
**Riesgo**: Inconsistencias si no se congela la tasa  
**Solución**: Tabla ExchangeRates + función helper

### Hotspot 5: Payment Confirmation Trigger
**Ubicación**: Webhook de Supabase o endpoint de pago  
**Problema**: ¿Cómo detectar cuándo se confirma un pago?  
**Crítico**: Determina cuándo calcular comisiones  
**Riesgo**: Perder eventos de pago = comisiones no calculadas  
**Solución**: Webhook + retry mechanism + idempotencia

### Hotspot 6: Distinción Kits vs Productos
**Ubicación**: `models/products.py`, lógica de comisiones  
**Problema**: Los kits NO generan VN, solo productos regulares  
**Crítico**: Afecta qué comisiones se pagan  
**Riesgo**: Pagar comisiones incorrectas  
**Solución**: Campo `product.presentation = 'kit'` + validación estricta

### Hotspot 7: Job de Cierre Mensual
**Ubicación**: `jobs/monthly_closure.py`  
**Problema**: ¿Qué pasa si el job falla o tarda más de 1 minuto?  
**Crítico**: Las comisiones deben calcularse una vez al mes  
**Riesgo**: Comisiones duplicadas o no calculadas  
**Solución**: Idempotencia + lock distribuido + status en Periods

### Hotspot 8: Timezone Management
**Ubicación**: Todos los timestamps  
**Problema**: México tiene cambio de horario de verano  
**Crítico**: Determina a qué período pertenece una transacción  
**Riesgo**: Transacciones asignadas al mes incorrecto  
**Solución**: SIEMPRE UTC en DB, convertir en UI

---

## 📝 Instrucciones para la IA

### Contexto Previo
Antes de empezar, revisa estos archivos en el proyecto:
1. `README.md` - Arquitectura de todo el proyecto
2. `DB_MLM_README.md` - Arquitectura completa
3. `MLM_SCHEME_README.md` - Reglas de negocio
4. Todos los archivos en `database/` - Tablas existentes
5. Estructura actual de carpetas del proyecto

### Enfoque de Implementación
1. **NO hagas todo de golpe** - Implementa por fases
2. **Pregunta antes de decidir** - Especialmente en los Hotspots
3. **Valida contra los READMEs** - Las reglas de negocio están documentadas
4. **Código limpio** - Type hints, docstrings, error handling
5. **Testing primero** - Tests unitarios antes de jobs complejos

### Preguntas Críticas a Resolver ANTES de Implementar

#### Pregunta 1: Arquitectura de Órdenes
¿Mantenemos `Transactions` separado de `Orders`, o consolidamos todo en `Orders + OrderItems`?

**Opción A**: Mantener ambas
```
Orders (encabezado) → OrderItems (líneas) → genera Transactions al confirmar pago
```

**Opción B**: Consolidar
```
Orders (encabezado) → OrderItems (líneas) [eliminar Transactions]
```

#### ✅ Pregunta 2: Momento de Inserción en UserTreePath
**DECISIÓN CONFIRMADA**: Opción B - **Al confirmar registro** (transacción atómica)
- Los registros en `UserTreePath` se crean INMEDIATAMENTE al confirmar el registro del usuario
- NO se requiere validación de email para activar la estructura de red
- NO se requiere pago previo para crear la genealogía
- Implementar en transacción atómica: `INSERT INTO users + INSERT INTO usertreepaths`

#### ✅ Pregunta 3: Caching de PVG (Puntos de Volumen Grupal)
**DECISIÓN CONFIRMADA**: Opción A - **Cálculo en tiempo real siempre**
- El PVG se calcula dinámicamente mediante query cada vez que se necesita
- NO pre-calcular ni almacenar en campo denormalizado
- Query optimizado con índices apropiados en `UserTreePath` y `Orders`
- Priorizar precisión sobre velocidad

#### ✅ Pregunta 4: Manejo de Webhooks de Pago
**DECISIÓN CONFIRMADA**: Opción C - **Ambos métodos**
- **Primario**: Webhook automático desde proveedor de pagos (Stripe/PayPal)
- **Fallback**: Confirmación manual por admin si webhook falla o no llega
- Implementar mecanismo de retry para webhooks perdidos
- Estado `PENDING_PAYMENT` → `PAYMENT_CONFIRMED` mediante ambos métodos

---

## 🎯 Priorización de Tareas

### Prioridad 1 (Crítica - Bloquea todo)
1. Decidir arquitectura Orders vs Transactions
2. Crear tabla Orders + OrderItems
3. Implementar UserTreePath en registro de usuarios
4. Función helper: get_upline() y get_downline()

### Prioridad 2 (Alta - Necesaria para MVP)
5. Implementar cálculo de PV y VG
6. Implementar detección de cambio de rango
7. Implementar Bono Rápido (trigger al pagar kit)
8. Tabla y función de tasas de cambio

### Prioridad 3 (Media - Lanzamiento completo)
9. Implementar cálculo de Bono Uninivel
10. Job de cierre mensual
11. Implementar Bono Matching
12. Implementar Bono por Alcance

### Prioridad 4 (Baja - Puede esperar)
13. Bono de Automóvil
14. Sistema de puntos NN Travels
15. Bono Cashback
16. Bono de Lealtad

---

## 🚀 Entregables Esperados

### Por Cada Fase
1. **Código Python** comentado con docstrings
2. **Tests unitarios** mínimos (happy path + edge cases)
3. **Migration script** de Supabase (si aplica)
4. **Documentación** de decisiones técnicas tomadas

### Estructura de Respuesta Ideal
```
## Fase X: [Nombre]

### Decisiones Técnicas
- [Decisión 1]: [Razón]
- [Decisión 2]: [Razón]

### Código Implementado
[código con comentarios]

### Queries SQL Optimizados
[queries críticos con EXPLAIN]

### Tests
[tests básicos]

### Siguientes Pasos
[qué hacer después]
```

---

## ⚠️ Red Flags a Evitar

1. ❌ **NO implementar lógica en el frontend** - Todo en backend
2. ❌ **NO hacer queries recursivos** - Usar UserTreePath correctamente
3. ❌ **NO hardcodear valores** - Usar tablas de configuración
4. ❌ **NO asumir timezone local** - SIEMPRE UTC en DB
5. ❌ **NO calcular comisiones sin validar pago confirmado**
6. ❌ **NO mezclar kits con productos** en queries de VN
7. ❌ **NO olvidar índices** en columnas de FK y filtros frecuentes
8. ❌ **NO hacer bulk inserts sin idempotencia** en jobs críticos

---

## 📊 Métricas de Éxito

- ✅ Orden completa desde carrito hasta pago en <2 segundos
- ✅ Bono Rápido calculado en <100ms al confirmar pago
- ✅ Job mensual completa en <5 minutos para 50k usuarios
- ✅ Query de genealogía (10 niveles) en <50ms
- ✅ Cálculo de VG en <100ms
- ✅ 0 comisiones duplicadas
- ✅ 0 comisiones perdidas

---

## 🔍 Testing Scenarios Críticos

### Scenario 1: Primera Compra de Kit
```python
# Usuario nuevo compra Full Protect
# Debe:
# - Crear orden
# - Confirmar pago
# - Generar 3 comisiones Bono Rápido (niveles 1-3)
# - Actualizar PV del usuario
# - Recalcular VG de toda la upline
# - Verificar si alcanzó Rango Visionario
```

### Scenario 2: Compra Internacional
```python
# Mexicano tiene directo Colombiano
# Colombiano compra producto regular
# Debe:
# - Calcular comisión en COP
# - Convertir a MXN con tasa fija
# - Guardar ambos montos + tasa usada
```

### Scenario 3: Cierre Mensual
```python
# Día 31 a las 23:59:59
# Debe:
# - Procesar TODOS los usuarios activos
# - Calcular Uninivel por niveles según rango
# - Calcular Matching para Embajadores
# - Generar snapshots
# - Marcar período como "closed"
# - No duplicar si se ejecuta 2 veces
```

---

## 📚 Recursos de Referencia

### Documentación Oficial
- Reflex: https://reflex.dev/docs/
- SQLModel: https://sqlmodel.tiangolo.com/
- Supabase Python: https://supabase.com/docs/reference/python/

### Patrones Relevantes
- Path Enumeration: Para UserTreePath
- Command Pattern: Para comisiones
- Observer Pattern: Para triggers de pago
- Strategy Pattern: Para diferentes tipos de bonos

---

**Última actualización**: Septiembre 2025  
**Versión del Prompt**: 1.0  
**Proyecto**: NN Protect MLM System
```