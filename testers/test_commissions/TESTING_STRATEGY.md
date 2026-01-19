# ESTRATEGIA DE TESTING FUNCIONAL - SISTEMA DE COMISIONES MLM

**Fecha**: Octubre 2, 2025
**Proyecto**: NNProtect Backoffice MLM
**Responsable**: QA Engineer Giovann
**Objetivo**: Validación funcional completa del sistema de comisiones antes de producción

---

## 📋 TABLA DE CONTENIDOS

1. [Alcance del Testing](#alcance-del-testing)
2. [Arquitectura de Tests](#arquitectura-de-tests)
3. [Bonos a Validar](#bonos-a-validar)
4. [Casos de Prueba Críticos](#casos-de-prueba-críticos)
5. [Fixtures y Factories](#fixtures-y-factories)
6. [Estructura de Archivos](#estructura-de-archivos)
7. [Matriz de Cobertura](#matriz-de-cobertura)
8. [Ejecución de Tests](#ejecución-de-tests)

---

## 1. ALCANCE DEL TESTING

### Servicios bajo Testing
- ✅ **CommissionService** - Cálculo de 5 bonos implementados
- ✅ **RankService** - Sistema automático de rangos
- ✅ **GenealogyService** - Estructura de red MLM
- ✅ **PVUpdateService** - Actualización de cache PV/PVG
- ✅ **ExchangeService** - Conversión de monedas
- ✅ **WalletService** - Billetera digital
- ✅ **PeriodService** - Gestión de períodos mensuales

### Bonos Implementados a Validar (5 de 9)
1. ✅ **Bono Rápido** (Fast Start Bonus) - 30%/10%/5% en kits
2. ✅ **Bono Uninivel** (Unilevel Bonus) - Mensual, 10 niveles
3. ✅ **Bono por Alcance** (Achievement Bonus) - One-time al subir rango
4. ✅ **Bono Matching** - 30%-5% sobre uninivel (solo Embajadores)
5. ✅ **Bono Directo** - 25% del VN en ventas directas

### Reglas Críticas de Negocio
- ⚠️ **Kits generan PV pero NO VN** (solo pagan Bono Rápido)
- ⚠️ **Productos generan PV y VN** (pagan todos los bonos)
- ⚠️ **payment_confirmed_at determina el período** (NO created_at)
- ⚠️ **Los rangos NUNCA retroceden**
- ⚠️ **PV mínimo: 1,465 para todos los rangos**
- ⚠️ **Conversión de monedas con tasas fijas** (NO market rates)

---

## 2. ARQUITECTURA DE TESTS

### Pirámide de Testing

```
                    /\
                   /  \
                  / E2E \         10% - Flujos completos end-to-end
                 /------\
                /        \
               / INTEGRA-\       30% - Tests de integración entre servicios
              /    CIÓN   \
             /------------\
            /              \
           /   UNITARIOS    \    60% - Tests unitarios de lógica de negocio
          /------------------\
```

### Tipos de Tests

#### 1. Tests Unitarios (60%)
- **Objetivo**: Validar lógica de negocio aislada
- **Scope**: Métodos individuales de servicios
- **Ejemplos**:
  - `CommissionService.process_fast_start_bonus()` con datos mockeados
  - `RankService.calculate_rank()` con PV/PVG específicos
  - `ExchangeService.convert_amount()` con tasas fijas

#### 2. Tests de Integración (30%)
- **Objetivo**: Validar interacción entre servicios
- **Scope**: Múltiples servicios trabajando juntos
- **Ejemplos**:
  - Orden confirmada → PV actualizado → Rango promovido → Comisión calculada
  - Usuario registrado → Genealogía creada → Sponsor en nivel 1
  - Comisión calculada → Depositada en wallet → Balance actualizado

#### 3. Tests End-to-End (10%)
- **Objetivo**: Validar flujos completos de usuario
- **Scope**: Desde acción de usuario hasta resultado final
- **Ejemplos**:
  - Usuario registra → Compra kit → Confirma pago → Genera comisiones a 3 niveles
  - Usuario alcanza PVG requerido → Rango promovido → Achievement Bonus pagado
  - Cierre de período → Cálculo uninivel → Depósito en wallets

---

## 3. BONOS A VALIDAR

### 3.1 BONO RÁPIDO (Fast Start Bonus)
**Estado**: ✅ Implementado
**Archivo de Test**: `test_fast_start_bonus.py`

#### Reglas de Negocio
- Aplica solo para productos con `presentation = "kit"`
- Paga 30%/10%/5% del PV del kit a niveles 1/2/3
- Instantáneo al confirmar pago
- Conversión a moneda del patrocinador
- Si no hay 3 niveles completos, solo paga los disponibles

#### Casos de Prueba
```python
✅ test_fast_bonus_with_3_levels_complete
✅ test_fast_bonus_with_only_2_levels
✅ test_fast_bonus_with_no_sponsor
✅ test_fast_bonus_multiple_kits_same_order
✅ test_fast_bonus_currency_conversion_mx_to_usa
✅ test_fast_bonus_not_triggered_by_products
✅ test_fast_bonus_percentages_accuracy
```

### 3.2 BONO UNINIVEL (Unilevel Bonus)
**Estado**: ✅ Implementado
**Archivo de Test**: `test_unilevel_bonus.py`

#### Reglas de Negocio
- Solo productos regulares (NO kits) generan VN para Uninivel
- Porcentajes según rango del miembro
- Hasta 10 niveles de profundidad (Embajadores: nivel 10+ infinito)
- Cálculo mensual (día 31)
- Basado en VN de órdenes confirmadas del período

#### Casos de Prueba
```python
✅ test_uninivel_visionario_3_levels
✅ test_uninivel_creativo_5_levels
✅ test_uninivel_embajador_solidario_10plus_levels
✅ test_uninivel_only_products_generate_vn
✅ test_uninivel_kits_excluded
✅ test_uninivel_multi_country_conversion
✅ test_uninivel_period_isolation
✅ test_uninivel_zero_commission_if_no_sales
```

### 3.3 BONO POR ALCANCE (Achievement Bonus)
**Estado**: ✅ Implementado
**Archivo de Test**: `test_achievement_bonus.py`

#### Reglas de Negocio
- Se paga UNA SOLA VEZ por cada rango alcanzado
- Rango Emprendedor: máximo 30 días desde inscripción
- Montos fijos por país según rango
- Trigger automático al promover rango

#### Casos de Prueba
```python
✅ test_achievement_bonus_first_time_emprendedor
✅ test_achievement_bonus_not_paid_second_time
✅ test_achievement_bonus_emprendedor_30_day_limit
✅ test_achievement_bonus_creativo_no_time_limit
✅ test_achievement_bonus_multi_currency
✅ test_achievement_bonus_embajador_solidario
✅ test_achievement_bonus_rank_never_regresses
```

### 3.4 BONO MATCHING
**Estado**: ✅ Implementado
**Archivo de Test**: `test_matching_bonus.py`

#### Reglas de Negocio
- Solo elegible para rangos Embajador (Transformador+)
- Se calcula sobre comisiones Uninivel de miembros Embajador en el equipo
- Porcentajes: 30%/20%/10%/5% según rango y profundidad
- Mensual (después de calcular Uninivel)

#### Casos de Prueba
```python
✅ test_matching_bonus_embajador_transformador_1_level
✅ test_matching_bonus_embajador_solidario_4_levels
✅ test_matching_not_eligible_if_not_ambassador
✅ test_matching_only_on_ambassadors_uninivel
✅ test_matching_requires_uninivel_calculated_first
✅ test_matching_multi_level_cascading
```

### 3.5 BONO DIRECTO (Direct Bonus)
**Estado**: ✅ Implementado
**Archivo de Test**: `test_direct_bonus.py`

#### Reglas de Negocio
- 25% del VN total de la orden
- Solo al patrocinador directo (sponsor_id)
- Aplica tanto para kits como productos regulares
- Conversión a moneda del patrocinador

#### Casos de Prueba
```python
✅ test_direct_bonus_25_percent_of_vn
✅ test_direct_bonus_on_kit_purchase
✅ test_direct_bonus_on_product_purchase
✅ test_direct_bonus_no_sponsor
✅ test_direct_bonus_currency_conversion
✅ test_direct_bonus_multiple_orders
```

---

## 4. CASOS DE PRUEBA CRÍTICOS

### 4.1 Edge Cases de Genealogía

#### Test: Red sin 3 niveles completos
```python
def test_fast_bonus_incomplete_upline():
    """
    Escenario:
        A → B (solo 2 niveles)

    Acción: B compra kit Full Protect (5,790 MXN, PV=2,930)

    Esperado:
        - A recibe 30% (879 PV) ✅
        - Nivel 2 no existe, no se paga ✅
        - Nivel 3 no existe, no se paga ✅
    """
```

#### Test: Red profunda (10+ niveles)
```python
def test_uninivel_deep_network_10plus_levels():
    """
    Escenario:
        A (Embajador Solidario) → B → C → ... → K (nivel 10) → L (nivel 11)

    Acción: Todos compran productos en el mes

    Esperado:
        - A recibe comisiones de niveles 1-9 con % específicos
        - A recibe comisión de nivel 10+ (todos desde nivel 10 al infinito) ✅
        - Total niveles 10+: L + todos después de L ✅
    """
```

#### Test: Red amplia (100+ directos)
```python
def test_uninivel_wide_network_100_direct_referrals():
    """
    Escenario:
        A (Creativo, 5 niveles) → 100 directos (B1...B100)

    Acción: Todos los 100 directos compran productos

    Esperado:
        - A recibe 5% sobre TODOS los 100 directos (nivel 1) ✅
        - Performance: Query debe completar en < 2 segundos ✅
    """
```

### 4.2 Edge Cases de Períodos

#### Test: Orden creada en mes anterior, pagada en mes actual
```python
def test_period_assignment_by_payment_confirmed_at():
    """
    Escenario:
        - Orden creada: 2025-09-30 23:59 UTC (created_at)
        - Pago confirmado: 2025-10-01 00:05 UTC (payment_confirmed_at)

    Esperado:
        - period_id = Octubre 2025 ✅
        - PV cuenta para Octubre ✅
        - Comisiones asignadas a Octubre ✅
    """
```

#### Test: Cambio de rango a mitad de mes
```python
def test_rank_change_mid_month_uninivel_calculation():
    """
    Escenario:
        - Usuario es Visionario (3 niveles) el día 1
        - Alcanza Creativo (5 niveles) el día 15
        - Compras en la red: Día 5 (Visionario), Día 20 (Creativo)

    Esperado:
        - Uninivel del mes se calcula con RANGO MÁS ALTO del mes ✅
        - Comisiones de niveles 4-5 solo desde día 15+ ✅
    """
```

### 4.3 Edge Cases de Monedas

#### Test: Red internacional (MX → USA → COL)
```python
def test_multi_country_commission_cascading():
    """
    Escenario:
        A (México, MXN) → B (USA, USD) → C (Colombia, COP)

    Acción: C compra kit Full Protect (COL: 1,300,000 COP)

    Esperado:
        - B recibe 30% en USD (convertido de COP) ✅
        - A recibe 10% en MXN (convertido de COP) ✅
        - Exchange rates guardados en commissions ✅
        - Conversión usa tasas fijas de la empresa ✅
    """
```

### 4.4 Edge Cases de Productos

#### Test: Kit vs Producto en mismo orden
```python
def test_mixed_order_kit_and_products():
    """
    Escenario:
        Orden con:
        - 1x Kit Full Protect (genera PV, NO VN)
        - 2x DNA 60 Cápsulas (genera PV y VN)

    Esperado:
        - total_pv = Kit PV + Productos PV ✅
        - total_vn = 0 (Kit) + Productos VN ✅
        - Bono Rápido: Solo sobre kit ✅
        - Bono Directo: 25% del VN de productos ✅
        - Bono Uninivel: Solo sobre VN de productos ✅
    """
```

### 4.5 Edge Cases de Datos

#### Test: NULL values y boundaries
```python
def test_commission_with_zero_amounts():
    """Validar que comisiones de 0 no se crean"""

def test_commission_with_null_sponsor():
    """Validar que usuario sin sponsor no genera comisiones upline"""

def test_commission_decimal_precision():
    """Validar que comisiones tienen precisión de 2 decimales"""

def test_commission_negative_amounts_rejected():
    """Validar que montos negativos lanzan error"""
```

---

## 5. FIXTURES Y FACTORIES

### Fixtures Reutilizables

#### 5.1 Database Session
```python
@pytest.fixture
def db_session():
    """Sesión de BD limpia para cada test"""
    with Session(engine) as session:
        yield session
        session.rollback()
```

#### 5.2 Test Users Factory
```python
@pytest.fixture
def test_users_network(db_session):
    """
    Crea red de prueba:
    A → B → C → D
    """
    users = {
        'A': create_test_user(member_id=1000, sponsor_id=None),
        'B': create_test_user(member_id=1001, sponsor_id=1000),
        'C': create_test_user(member_id=1002, sponsor_id=1001),
        'D': create_test_user(member_id=1003, sponsor_id=1002),
    }
    return users
```

#### 5.3 Test Products Factory
```python
@pytest.fixture
def test_kit_full_protect(db_session):
    """Kit Full Protect con PV pero sin VN"""
    return Products(
        SKU="KIT-FULL",
        product_name="Full Protect Kit",
        presentation="kit",
        type="kit",
        pv_mx=2930,
        vn_mx=0,  # ⚠️ CRÍTICO: Kits NO generan VN
        price_mx=5790
    )

@pytest.fixture
def test_product_dna_60(db_session):
    """Producto DNA 60 con PV y VN"""
    return Products(
        SKU="DNA-60",
        product_name="DNA 60 Cápsulas",
        presentation="capsulas",
        type="suplemento",
        pv_mx=1465,
        vn_mx=1465,  # ✅ Productos SÍ generan VN
        price_mx=2490
    )
```

#### 5.4 Test Orders Factory
```python
@pytest.fixture
def create_test_order():
    """Factory function para crear órdenes de prueba"""
    def _create_order(
        member_id: int,
        products: List[Tuple[Products, int]],  # (product, quantity)
        payment_confirmed: bool = True
    ) -> Orders:
        order = Orders(
            member_id=member_id,
            country="Mexico",
            currency="MXN",
            status=OrderStatus.PAYMENT_CONFIRMED.value if payment_confirmed else OrderStatus.DRAFT.value,
            payment_confirmed_at=datetime.now(timezone.utc) if payment_confirmed else None
        )
        # ... calcular totales
        return order

    return _create_order
```

#### 5.5 Test Periods Factory
```python
@pytest.fixture
def test_period_current(db_session):
    """Período actual de prueba"""
    period = Periods(
        name="Test Period Oct 2025",
        starts_on=datetime(2025, 10, 1, tzinfo=timezone.utc),
        ends_on=datetime(2025, 10, 31, 23, 59, 59, tzinfo=timezone.utc),
        closed_at=None  # Activo
    )
    db_session.add(period)
    db_session.flush()
    return period
```

---

## 6. ESTRUCTURA DE ARCHIVOS

```
testers/test_commissions/
│
├── TESTING_STRATEGY.md                 # Este documento
├── README.md                            # Guía rápida de ejecución
├── pytest.ini                           # Configuración de pytest
├── conftest.py                          # Fixtures compartidas
│
├── fixtures/                            # Fixtures reutilizables
│   ├── __init__.py
│   ├── db_fixtures.py                   # Sesiones de BD
│   ├── user_fixtures.py                 # Usuarios y genealogía
│   ├── product_fixtures.py              # Productos y kits
│   ├── order_fixtures.py                # Órdenes de prueba
│   └── period_fixtures.py               # Períodos mensuales
│
├── factories/                           # Factories de datos
│   ├── __init__.py
│   ├── user_factory.py                  # UserFactory
│   ├── product_factory.py               # ProductFactory
│   ├── order_factory.py                 # OrderFactory
│   └── network_factory.py               # NetworkFactory (redes complejas)
│
├── unit/                                # Tests unitarios (60%)
│   ├── __init__.py
│   ├── test_fast_start_bonus.py         # Bono Rápido
│   ├── test_unilevel_bonus.py           # Bono Uninivel
│   ├── test_achievement_bonus.py        # Bono por Alcance
│   ├── test_matching_bonus.py           # Bono Matching
│   ├── test_direct_bonus.py             # Bono Directo
│   ├── test_rank_service.py             # Sistema de rangos
│   ├── test_pv_update_service.py        # Actualización PV/PVG
│   ├── test_exchange_service.py         # Conversión de monedas
│   └── test_genealogy_service.py        # Estructura de red
│
├── integration/                         # Tests de integración (30%)
│   ├── __init__.py
│   ├── test_order_to_commission_flow.py # Orden → Comisión
│   ├── test_rank_promotion_flow.py      # Promoción → Achievement
│   ├── test_period_closure_flow.py      # Cierre → Uninivel
│   └── test_wallet_commission_flow.py   # Comisión → Wallet
│
├── e2e/                                 # Tests end-to-end (10%)
│   ├── __init__.py
│   ├── test_new_user_first_purchase.py  # Registro → Compra → Comisiones
│   ├── test_rank_progression.py         # Progresión completa de rangos
│   └── test_monthly_commission_cycle.py # Ciclo completo mensual
│
├── edge_cases/                          # Edge cases críticos
│   ├── __init__.py
│   ├── test_genealogy_edge_cases.py     # Red incompleta, profunda, amplia
│   ├── test_period_edge_cases.py        # Cambio de mes, rango a mitad
│   ├── test_currency_edge_cases.py      # Multi-país, conversión
│   └── test_data_edge_cases.py          # NULL, zeros, boundaries
│
├── regression/                          # Tests de regresión
│   ├── __init__.py
│   ├── test_existing_commissions.py     # Validar comisiones existentes
│   └── test_database_migrations.py      # Validar migraciones
│
├── performance/                         # Tests de performance
│   ├── __init__.py
│   ├── test_large_network_queries.py    # Redes de 50k+ usuarios
│   └── test_batch_calculations.py       # Cálculos masivos
│
└── helpers/                             # Funciones helper
    ├── __init__.py
    ├── assertions.py                    # Asserts personalizados
    ├── validators.py                    # Validadores de datos
    └── test_data_cleanup.py             # Limpieza de datos de prueba
```

---

## 7. MATRIZ DE COBERTURA

### Cobertura por Servicio

| Servicio | Tests Unitarios | Tests Integración | Cobertura Objetivo | Estado |
|----------|----------------|-------------------|-------------------|--------|
| CommissionService | 35 tests | 10 tests | 95% | 🟡 En progreso |
| RankService | 20 tests | 8 tests | 95% | 🟡 En progreso |
| GenealogyService | 15 tests | 5 tests | 90% | 🟡 En progreso |
| PVUpdateService | 12 tests | 6 tests | 90% | 🟡 En progreso |
| ExchangeService | 10 tests | 3 tests | 95% | 🟡 En progreso |
| WalletService | 18 tests | 7 tests | 95% | 🟡 En progreso |
| PeriodService | 8 tests | 4 tests | 90% | 🟡 En progreso |

### Cobertura por Bono

| Bono | Casos Base | Edge Cases | Performance | Total | Estado |
|------|-----------|-----------|-------------|-------|--------|
| Bono Rápido | 7 tests | 5 tests | 2 tests | 14 | 🟡 |
| Bono Uninivel | 8 tests | 8 tests | 3 tests | 19 | 🟡 |
| Bono Alcance | 7 tests | 4 tests | 1 test | 12 | 🟡 |
| Bono Matching | 6 tests | 4 tests | 2 tests | 12 | 🟡 |
| Bono Directo | 6 tests | 3 tests | 1 test | 10 | 🟡 |

---

## 8. EJECUCIÓN DE TESTS

### Comandos Básicos

```bash
# Ejecutar todos los tests
pytest testers/test_commissions/

# Ejecutar solo tests unitarios
pytest testers/test_commissions/unit/

# Ejecutar solo tests de un bono específico
pytest testers/test_commissions/unit/test_fast_start_bonus.py

# Ejecutar con verbose output
pytest testers/test_commissions/ -v

# Ejecutar con coverage report
pytest testers/test_commissions/ --cov=NNProtect_new_website.modules.network.backend --cov-report=html

# Ejecutar tests marcados como críticos
pytest testers/test_commissions/ -m critical

# Ejecutar tests en paralelo (más rápido)
pytest testers/test_commissions/ -n auto
```

### Markers Personalizados

```python
@pytest.mark.critical  # Tests críticos que DEBEN pasar
@pytest.mark.edge_case  # Edge cases
@pytest.mark.slow  # Tests lentos (> 5 segundos)
@pytest.mark.integration  # Tests de integración
@pytest.mark.e2e  # Tests end-to-end
```

### Configuración en pytest.ini

```ini
[pytest]
testpaths = testers/test_commissions
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    critical: Tests críticos que bloquean producción
    edge_case: Edge cases específicos
    slow: Tests que toman más de 5 segundos
    integration: Tests de integración entre servicios
    e2e: Tests end-to-end completos
    regression: Tests de regresión

addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
```

---

## 9. CHECKLIST DE VALIDACIÓN

### Pre-Producción Checklist

#### Bono Rápido ✅
- [ ] 30%/10%/5% correctos en 3 niveles
- [ ] Solo aplica para kits (presentation="kit")
- [ ] Conversión de monedas correcta
- [ ] Funciona con upline incompleto (1-2 niveles)
- [ ] No se activa con productos regulares

#### Bono Uninivel ✅
- [ ] Porcentajes por rango correctos
- [ ] Solo productos generan VN (kits excluidos)
- [ ] Funciona hasta nivel 10+
- [ ] Cálculo mensual correcto
- [ ] Period isolation (no mezcla meses)
- [ ] Performance con redes grandes (50k+ usuarios)

#### Bono por Alcance ✅
- [ ] Se paga solo UNA VEZ por rango
- [ ] Límite de 30 días para Emprendedor
- [ ] Montos correctos por país
- [ ] Trigger automático al promover
- [ ] No se paga si ya se cobró antes

#### Bono Matching ✅
- [ ] Solo para rangos Embajador
- [ ] Porcentajes 30%/20%/10%/5% correctos
- [ ] Solo sobre uninivel de Embajadores descendientes
- [ ] Cálculo después de Uninivel

#### Bono Directo ✅
- [ ] 25% del VN correcto
- [ ] Aplica tanto para kits como productos
- [ ] Conversión de monedas correcta
- [ ] Solo al patrocinador directo

#### Sistema de Rangos ✅
- [ ] PV mínimo 1,465 verificado
- [ ] PVG por rango correcto
- [ ] Rangos nunca retroceden
- [ ] Promoción automática funciona
- [ ] Historial de rangos preservado

#### Períodos ✅
- [ ] payment_confirmed_at determina período
- [ ] PV/PVG reset día 1 del mes
- [ ] Cierre automático último día
- [ ] Período actual correctamente identificado

#### Conversión de Monedas ✅
- [ ] Tasas fijas de la empresa (NO market)
- [ ] Exchange rate guardado en comisión
- [ ] Soporte multi-país (MX/USA/COL)

#### Wallet ✅
- [ ] Comisiones depositadas correctamente
- [ ] Balance nunca negativo
- [ ] Transacciones inmutables
- [ ] UUID para idempotencia

---

## 10. PRÓXIMOS PASOS

### Fase 1: Setup (Completar en 1 día)
1. ✅ Crear estructura de directorios
2. ✅ Documentar estrategia (este archivo)
3. 🟡 Implementar fixtures base
4. 🟡 Implementar factories
5. 🟡 Configurar pytest.ini

### Fase 2: Tests Unitarios (Completar en 3 días)
1. 🟡 Implementar tests de Bono Rápido (7 tests)
2. 🟡 Implementar tests de Bono Uninivel (8 tests)
3. 🟡 Implementar tests de Bono por Alcance (7 tests)
4. 🟡 Implementar tests de Bono Matching (6 tests)
5. 🟡 Implementar tests de Bono Directo (6 tests)

### Fase 3: Tests de Integración (Completar en 2 días)
1. 🟡 Flujo Orden → Comisión
2. 🟡 Flujo Rango → Achievement
3. 🟡 Flujo Período → Uninivel
4. 🟡 Flujo Comisión → Wallet

### Fase 4: Edge Cases (Completar en 2 días)
1. 🟡 Edge cases de genealogía
2. 🟡 Edge cases de períodos
3. 🟡 Edge cases de monedas
4. 🟡 Edge cases de datos

### Fase 5: Validación Final (Completar en 1 día)
1. 🟡 Ejecutar suite completa
2. 🟡 Generar reporte de coverage
3. 🟡 Validar checklist pre-producción
4. 🟡 Documentar issues encontrados

---

## 📞 CONTACTO

**QA Engineer**: Giovann
**Proyecto**: NNProtect Backoffice MLM
**Fecha**: Octubre 2025

Para consultas o issues encontrados durante testing, documentar en:
- `/testers/test_commissions/ISSUES_LOG.md`
