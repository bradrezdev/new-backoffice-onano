# Testing Funcional del Sistema de Comisiones MLM

**Proyecto**: NNProtect Backoffice MLM
**QA Engineer**: Giovann
**Fecha**: Octubre 2025
**Estado**: En Desarrollo

---

## 📋 DESCRIPCIÓN GENERAL

Suite completa de tests funcionales para validar el cálculo correcto de comisiones del sistema MLM de NNProtect antes de ir a producción.

### Alcance
- ✅ 5 Bonos Implementados (Rápido, Uninivel, Alcance, Matching, Directo)
- ✅ Sistema de Rangos (9 rangos)
- ✅ Genealogía MLM (Path Enumeration)
- ✅ Conversión de Monedas (MXN, USD, COP)
- ✅ Gestión de Períodos Mensuales
- ✅ Wallet Digital

---

## 🚀 INICIO RÁPIDO

### 1. Instalación

```bash
# Navegar al directorio del proyecto
cd /Users/bradrez/Documents/NNProtect_new_website

# Activar entorno virtual (si existe)
source nnprotect_backoffice/bin/activate

# Instalar pytest y dependencias
pip install pytest pytest-cov pytest-xdist sqlmodel
```

### 2. Ejecución de Tests

```bash
# Ejecutar TODOS los tests
pytest testers/test_commissions/ -v

# Ejecutar solo tests del Bono Rápido
pytest testers/test_commissions/unit/test_fast_start_bonus.py -v

# Ejecutar solo tests del Bono Directo
pytest testers/test_commissions/unit/test_direct_bonus.py -v

# Ejecutar solo tests críticos
pytest testers/test_commissions/ -m critical -v

# Ejecutar con reporte de cobertura
pytest testers/test_commissions/ --cov=NNProtect_new_website.modules.network.backend --cov-report=html

# Ejecutar en paralelo (más rápido)
pytest testers/test_commissions/ -n auto -v
```

### 3. Ver Resultados

```bash
# Abrir reporte de cobertura (si se generó)
open htmlcov/index.html
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
testers/test_commissions/
│
├── README.md                           # Este archivo
├── TESTING_STRATEGY.md                 # Estrategia completa de testing
├── pytest.ini                          # Configuración de pytest
├── conftest.py                         # Fixtures compartidas
│
├── unit/                               # Tests unitarios
│   ├── test_fast_start_bonus.py        # ✅ Bono Rápido (9 tests)
│   ├── test_direct_bonus.py            # ✅ Bono Directo (7 tests)
│   ├── test_unilevel_bonus.py          # 🟡 Bono Uninivel (pendiente)
│   ├── test_achievement_bonus.py       # 🟡 Bono Alcance (pendiente)
│   ├── test_matching_bonus.py          # 🟡 Bono Matching (pendiente)
│   ├── test_rank_service.py            # 🟡 Sistema de Rangos (pendiente)
│   └── test_exchange_service.py        # 🟡 Conversión Monedas (pendiente)
│
├── integration/                        # Tests de integración (pendiente)
├── e2e/                                # Tests end-to-end (pendiente)
├── edge_cases/                         # Edge cases críticos (pendiente)
└── helpers/                            # Helpers y validaciones (pendiente)
```

---

## ✅ TESTS IMPLEMENTADOS

### Bono Rápido (Fast Start Bonus) - 9 Tests ✅

| Test | Descripción | Estado |
|------|-------------|--------|
| `test_fast_bonus_with_3_levels_complete` | Valida 30%/10%/5% en 3 niveles | ✅ |
| `test_fast_bonus_with_only_2_levels` | Valida con solo 2 niveles upline | ✅ |
| `test_fast_bonus_with_no_sponsor` | Valida sin sponsor (no comisiones) | ✅ |
| `test_fast_bonus_multiple_kits_same_order` | Valida múltiples kits en orden | ✅ |
| `test_fast_bonus_currency_conversion_mx_to_usa` | Valida conversión MXN→USD | ✅ |
| `test_fast_bonus_not_triggered_by_products` | Valida que productos NO activan | ✅ |
| `test_fast_bonus_percentages_accuracy` | Valida precisión de porcentajes | ✅ |
| `test_fast_bonus_order_not_confirmed` | Valida orden sin confirmar | ✅ |

**Comandos:**
```bash
# Ejecutar todos los tests del Bono Rápido
pytest testers/test_commissions/unit/test_fast_start_bonus.py -v

# Ejecutar solo tests críticos del Bono Rápido
pytest testers/test_commissions/unit/test_fast_start_bonus.py -m critical -v
```

### Bono Directo (Direct Bonus) - 7 Tests ✅

| Test | Descripción | Estado |
|------|-------------|--------|
| `test_direct_bonus_25_percent_of_vn` | Valida 25% del VN correcto | ✅ |
| `test_direct_bonus_on_kit_purchase` | Valida en kits (VN=0) | ✅ |
| `test_direct_bonus_on_product_purchase` | Valida en productos regulares | ✅ |
| `test_direct_bonus_no_sponsor` | Valida sin sponsor | ✅ |
| `test_direct_bonus_currency_conversion` | Valida conversión de moneda | ✅ |
| `test_direct_bonus_multiple_orders` | Valida múltiples órdenes | ✅ |

**Comandos:**
```bash
# Ejecutar todos los tests del Bono Directo
pytest testers/test_commissions/unit/test_direct_bonus.py -v
```

---

## 🔍 CASOS DE PRUEBA CRÍTICOS

### 1. Kit vs Producto

**Regla Crítica**: Kits generan PV pero NO VN. Productos generan PV y VN.

```python
# Test: Validar que kits NO activen Bono Uninivel
pytest testers/test_commissions/unit/test_fast_start_bonus.py::TestFastStartBonus::test_fast_bonus_not_triggered_by_products -v
```

### 2. Conversión de Monedas

**Regla Crítica**: Usar tasas fijas de la empresa, NO market rates.

```python
# Test: Validar conversión MXN→USD→COP
pytest testers/test_commissions/unit/test_fast_start_bonus.py::TestFastStartBonus::test_fast_bonus_currency_conversion_mx_to_usa -v
```

### 3. Upline Incompleto

**Regla Crítica**: Si no hay 3 niveles upline, solo pagar los disponibles.

```python
# Test: Validar con solo 2 niveles
pytest testers/test_commissions/unit/test_fast_start_bonus.py::TestFastStartBonus::test_fast_bonus_with_only_2_levels -v
```

---

## 🎯 PRÓXIMOS PASOS

### Fase 1: Completar Tests Unitarios (3 días)
- [ ] Implementar `test_unilevel_bonus.py` (8 tests)
- [ ] Implementar `test_achievement_bonus.py` (7 tests)
- [ ] Implementar `test_matching_bonus.py` (6 tests)
- [ ] Implementar `test_rank_service.py` (10 tests)
- [ ] Implementar `test_exchange_service.py` (5 tests)

### Fase 2: Tests de Integración (2 días)
- [ ] Flujo Orden → Comisión
- [ ] Flujo Rango → Achievement
- [ ] Flujo Período → Uninivel
- [ ] Flujo Comisión → Wallet

### Fase 3: Edge Cases (2 días)
- [ ] Red incompleta (< 3 niveles)
- [ ] Red profunda (10+ niveles)
- [ ] Red amplia (100+ directos)
- [ ] Cambio de rango a mitad de mes
- [ ] Orden creada en mes anterior, pagada en mes actual
- [ ] Multi-país (MX → USA → COL)

### Fase 4: Validación Final (1 día)
- [ ] Ejecutar suite completa
- [ ] Generar reporte de coverage
- [ ] Validar checklist pre-producción
- [ ] Documentar issues encontrados

---

## 📊 COBERTURA DE CÓDIGO

### Objetivo
- **Servicios de Comisiones**: 95% de cobertura
- **Servicios de Rangos**: 95% de cobertura
- **Servicios de Genealogía**: 90% de cobertura
- **Total General**: 90%+ de cobertura

### Generar Reporte

```bash
# Generar reporte HTML
pytest testers/test_commissions/ --cov=NNProtect_new_website.modules.network.backend --cov-report=html

# Ver reporte en navegador
open htmlcov/index.html
```

---

## 🐛 ISSUES CONOCIDOS

### Issue #1: Kits con VN > 0 en BD
**Problema**: Algunos kits tienen `vn_mx > 0` en la tabla `products`.
**Impacto**: CRÍTICO - Kits NO deben generar VN.
**Solución**: Ejecutar UPDATE:
```sql
UPDATE products SET vn_mx = 0, vn_usa = 0, vn_colombia = 0 WHERE presentation = 'kit';
```

### Issue #2: Campo `is_kit` no existe
**Problema**: No hay campo booleano `is_kit` en tabla `products`.
**Impacto**: MEDIO - Se usa `presentation = 'kit'` como workaround.
**Solución**: Agregar campo en migración:
```sql
ALTER TABLE products ADD COLUMN is_kit BOOLEAN DEFAULT FALSE;
UPDATE products SET is_kit = TRUE WHERE presentation = 'kit';
```

---

## 📞 SOPORTE

### Documentación Adicional
- [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) - Estrategia completa de testing
- [/docs/CLAUDE.md](../../docs/CLAUDE.md) - Estado actual del proyecto
- [/docs/MLM_SCHEME_README.md](../../docs/MLM_SCHEME_README.md) - Plan de compensación MLM

### Contacto
**QA Engineer**: Giovann
**Email**: qa@nnprotect.com (placeholder)
**Fecha**: Octubre 2025

---

## 📝 CHANGELOG

### 2025-10-02
- ✅ Creada estructura de directorios
- ✅ Documentada estrategia completa (TESTING_STRATEGY.md)
- ✅ Implementadas fixtures base (conftest.py)
- ✅ Configurado pytest.ini
- ✅ Implementados tests del Bono Rápido (9 tests)
- ✅ Implementados tests del Bono Directo (7 tests)
- 🟡 Tests del Bono Uninivel (pendiente)
- 🟡 Tests del Bono por Alcance (pendiente)
- 🟡 Tests del Bono Matching (pendiente)

---

**Última Actualización**: Octubre 2, 2025
**Versión**: 1.0
**Estado**: 🟡 En Desarrollo (Fase 1 - 30% completado)
