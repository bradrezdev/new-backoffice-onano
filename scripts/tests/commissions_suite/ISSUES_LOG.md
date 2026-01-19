# ISSUES LOG - Testing del Sistema de Comisiones MLM

**Proyecto**: NNProtect Backoffice MLM
**QA Engineer**: Giovann
**Fecha Inicio**: Octubre 2, 2025

---

## 🔴 ISSUES CRÍTICOS (Bloquean Producción)

### Issue #001: Kits con VN > 0 en Base de Datos
**Fecha**: 2025-10-02
**Severidad**: 🔴 CRÍTICA
**Estado**: 🟡 PENDIENTE

**Descripción**:
Los productos tipo 'kit' en la tabla `products` tienen valores de VN (Valor Neto) mayores a 0, cuando según las reglas de negocio los kits NO deben generar VN.

**Regla de Negocio Violada**:
- ⚠️ Kits deben generar PV pero NO VN
- ⚠️ Solo productos regulares generan VN para comisiones Uninivel

**Impacto**:
- Los kits están generando comisiones de Bono Uninivel cuando NO deberían
- Cálculo de comisiones incorrecto
- Potencial pérdida financiera para la empresa

**Datos Actuales**:
```sql
SELECT SKU, product_name, presentation, vn_mx, vn_usa, vn_colombia
FROM products
WHERE presentation = 'kit';

-- Resultado: Kits con VN > 0 ❌
```

**Solución Propuesta**:
```sql
-- Actualizar todos los kits a VN = 0
UPDATE products
SET vn_mx = 0, vn_usa = 0, vn_colombia = 0
WHERE presentation = 'kit';

-- Verificar
SELECT COUNT(*) FROM products WHERE presentation = 'kit' AND (vn_mx > 0 OR vn_usa > 0 OR vn_colombia > 0);
-- Debe retornar 0
```

**Tests Afectados**:
- `test_fast_bonus_not_triggered_by_products` ✅ (detectó el issue)
- `test_unilevel_kits_excluded` 🟡 (pendiente)

**Responsable**: DB Admin
**Fecha Límite**: 2025-10-05

---

### Issue #002: Campo `is_kit` no existe en tabla products
**Fecha**: 2025-10-02
**Severidad**: 🟡 MEDIA
**Estado**: 🟡 PENDIENTE

**Descripción**:
No existe un campo booleano explícito `is_kit` en la tabla `products`. Actualmente se usa `presentation = 'kit'` como workaround.

**Regla de Negocio**:
- Necesitamos distinguir rápidamente kits de productos
- El campo `presentation` tiene múltiples valores ('kit', 'liquido', 'capsulas', etc.)

**Impacto**:
- Queries menos eficientes (string comparison vs boolean)
- Lógica de negocio menos clara
- Riesgo de errores si se agregan nuevas presentaciones

**Solución Propuesta**:
```sql
-- Agregar campo is_kit
ALTER TABLE products ADD COLUMN is_kit BOOLEAN DEFAULT FALSE;

-- Marcar kits existentes
UPDATE products SET is_kit = TRUE WHERE presentation = 'kit';

-- Crear índice para performance
CREATE INDEX idx_products_is_kit ON products(is_kit);
```

**Workaround Actual**:
```python
# En CommissionService.process_fast_start_bonus()
if product and product.presentation == "kit":
    kit_items.append((item, product))
```

**Responsable**: Backend Developer
**Fecha Límite**: 2025-10-10

---

### Issue #003: Campo `generates_vn` no existe en tabla products
**Fecha**: 2025-10-02
**Severidad**: 🟡 MEDIA
**Estado**: 🟡 PENDIENTE

**Descripción**:
No hay un campo booleano explícito `generates_vn` para indicar si un producto genera Valor Neto para comisiones.

**Regla de Negocio**:
- Kits: `generates_vn = FALSE`
- Productos: `generates_vn = TRUE`
- Debe ser explícito y validable

**Impacto**:
- Lógica de negocio implícita (se asume que si VN=0, no genera)
- Riesgo de errores si se crean productos con VN=0 que deberían generar VN

**Solución Propuesta**:
```sql
-- Agregar campo generates_vn
ALTER TABLE products ADD COLUMN generates_vn BOOLEAN DEFAULT TRUE;

-- Actualizar kits
UPDATE products SET generates_vn = FALSE WHERE presentation = 'kit';

-- Constraint para asegurar consistencia
ALTER TABLE products ADD CONSTRAINT check_vn_consistency
CHECK (
    (generates_vn = FALSE AND vn_mx = 0 AND vn_usa = 0 AND vn_colombia = 0) OR
    (generates_vn = TRUE)
);
```

**Responsable**: Backend Developer
**Fecha Límite**: 2025-10-10

---

## 🟡 ISSUES MEDIOS (Deben Resolverse Antes de Producción)

### Issue #004: Tasas de cambio no cargadas en BD
**Fecha**: 2025-10-02
**Severidad**: 🟡 MEDIA
**Estado**: 🟡 PENDIENTE

**Descripción**:
La tabla `exchange_rates` está vacía. Los tests usan fixture `setup_exchange_rates` para cargar tasas temporales.

**Regla de Negocio**:
- Usar tasas fijas de la empresa (NO market rates)
- Tasas deben estar vigentes antes de procesar comisiones

**Impacto**:
- Comisiones multi-país fallan sin tasas de cambio
- Tests pasan pero producción fallaría

**Solución Propuesta**:
```sql
-- Cargar tasas fijas de la empresa
INSERT INTO exchange_rates (from_currency, to_currency, rate, effective_from, notes)
VALUES
  ('MXN', 'USD', 0.055, '2025-01-01', 'Tasa fija empresa'),
  ('USD', 'MXN', 18.0, '2025-01-01', 'Tasa fija empresa'),
  ('MXN', 'COP', 225.0, '2025-01-01', 'Tasa fija empresa'),
  ('COP', 'MXN', 0.0044, '2025-01-01', 'Tasa fija empresa'),
  ('USD', 'COP', 4000.0, '2025-01-01', 'Tasa fija empresa'),
  ('COP', 'USD', 0.00025, '2025-01-01', 'Tasa fija empresa');
```

**Responsable**: Backend Developer
**Fecha Límite**: 2025-10-08

---

### Issue #005: Período actual no existe al iniciar sistema
**Fecha**: 2025-10-02
**Severidad**: 🟡 MEDIA
**Estado**: 🟡 PENDIENTE

**Descripción**:
Si se inicia el sistema sin un período activo, las comisiones fallan porque `period_id` es NULL.

**Regla de Negocio**:
- Siempre debe haber un período actual activo
- Los períodos se crean automáticamente el día 1 de cada mes

**Impacto**:
- Comisiones no se asignan a período
- Reportes de comisiones por mes fallan

**Solución Propuesta**:
1. Crear período actual manualmente:
```python
from NNProtect_new_website.modules.network.backend.period_service import PeriodService
PeriodService.create_monthly_period(year=2025, month=10)
```

2. O activar scheduler automático:
```python
from NNProtect_new_website.modules.network.backend.scheduler_service import SchedulerService
SchedulerService.start_scheduler()
```

**Responsable**: Backend Developer
**Fecha Límite**: 2025-10-08

---

## 🟢 ISSUES BAJOS (Mejoras Futuras)

### Issue #006: Tests sin paralelización
**Fecha**: 2025-10-02
**Severidad**: 🟢 BAJA
**Estado**: 🟡 PENDIENTE

**Descripción**:
Los tests se ejecutan secuencialmente. Con 120+ tests planeados, el tiempo de ejecución será largo.

**Solución Propuesta**:
```bash
# Instalar pytest-xdist
pip install pytest-xdist

# Ejecutar en paralelo
pytest testers/test_commissions/ -n auto
```

**Responsable**: QA Engineer
**Fecha Límite**: 2025-10-15

---

### Issue #007: Sin reporte de coverage automático
**Fecha**: 2025-10-02
**Severidad**: 🟢 BAJA
**Estado**: 🟡 PENDIENTE

**Descripción**:
No hay generación automática de reportes de cobertura en CI/CD.

**Solución Propuesta**:
```bash
# Agregar a pipeline CI/CD
pytest testers/test_commissions/ \
  --cov=NNProtect_new_website.modules.network.backend \
  --cov-report=html \
  --cov-report=xml \
  --cov-fail-under=90
```

**Responsable**: DevOps
**Fecha Límite**: 2025-10-20

---

## 📊 RESUMEN DE ISSUES

| Severidad | Total | Resueltos | Pendientes | % Completado |
|-----------|-------|-----------|------------|--------------|
| 🔴 CRÍTICA | 3 | 0 | 3 | 0% |
| 🟡 MEDIA | 2 | 0 | 2 | 0% |
| 🟢 BAJA | 2 | 0 | 2 | 0% |
| **TOTAL** | **7** | **0** | **7** | **0%** |

---

## 📝 TEMPLATE PARA NUEVOS ISSUES

```markdown
### Issue #XXX: [Título Descriptivo]
**Fecha**: YYYY-MM-DD
**Severidad**: 🔴 CRÍTICA / 🟡 MEDIA / 🟢 BAJA
**Estado**: 🟡 PENDIENTE / ✅ RESUELTO

**Descripción**:
[Descripción detallada del issue]

**Regla de Negocio Violada**:
- [Regla 1]
- [Regla 2]

**Impacto**:
[Impacto en el sistema]

**Solución Propuesta**:
[Código o pasos para resolver]

**Tests Afectados**:
- `test_nombre_1` ✅/🟡
- `test_nombre_2` ✅/🟡

**Responsable**: [Nombre]
**Fecha Límite**: YYYY-MM-DD
```

---

**Última Actualización**: 2025-10-02
**Próxima Revisión**: 2025-10-05
