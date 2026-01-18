# Documentación: Reinicio de Usuarios en Nuevos Períodos

## 🎯 Objetivo
Resetear automáticamente los datos de usuarios cada vez que se crea un nuevo período, garantizando que todos los usuarios comiencen desde cero en el nuevo ciclo.

## 📋 Datos que se Reinician

### Tabla `users`:
1. **status** → `NO_QUALIFIED`
   - Todos los usuarios vuelven a estado no calificado
   - Se actualizará a `QUALIFIED` cuando alcancen 1465 PV

2. **pv_cache** → `0`
   - Puntos de volumen personal a cero

3. **pvg_cache** → `0`
   - Puntos de volumen grupal a cero

4. **vn_cache** → `0.0`
   - Valor de negocio a cero

### Tabla `user_rank_history`:
- Se crea un nuevo registro para cada usuario con:
  - **rank_id** = `1` (rango inicial)
  - **period_id** = ID del nuevo período
  - **achieved_on** = timestamp actual (UTC)

## 🔧 Implementación

### 1. Método Centralizado
Se creó el método `PeriodService.reset_users_for_new_period()` en `period_service.py`:

```python
@classmethod
def reset_users_for_new_period(cls, session, new_period: Periods) -> bool:
    """
    Reinicia los datos de todos los usuarios para el nuevo período.
    
    - Resetea status, pv_cache, pvg_cache, vn_cache
    - Crea registro en user_rank_history con rank_id=1
    """
```

**Principios aplicados:**
- **KISS**: Una función, una responsabilidad clara
- **DRY**: Método reutilizable centralizado
- **POO**: Encapsulado dentro del servicio de períodos

### 2. Integración Automática

#### En `PeriodService.create_period_for_month()`:
```python
# Crear nuevo período
new_period = Periods(...)
session.add(new_period)
session.flush()

# ✅ Reiniciar usuarios automáticamente
cls.reset_users_for_new_period(session, new_period)

return new_period
```

#### En Admin Panel (`admin_state.py`):
```python
# Crear período desde admin
new_period = Periods(...)
session.add(new_period)
session.flush()

# ✅ Reiniciar usuarios automáticamente
from NNProtect_new_website.mlm_service.period_service import PeriodService
PeriodService.reset_users_for_new_period(session, new_period)

session.commit()
```

## ✅ Comportamiento Garantizado

### ✅ SIEMPRE se resetea cuando:
1. Se crea un período nuevo con `PeriodService.create_period_for_month()`
2. Se cierra un período y se crea uno nuevo desde el Admin Panel
3. Se usa cualquier método que cree un período por primera vez

### ✅ NUNCA se resetea cuando:
1. Se intenta crear un período que ya existe (retorna el existente)
2. Se consulta o modifica un período existente
3. Se finalizan períodos sin crear uno nuevo

## 🧪 Tests Realizados

### 1. `test_period_reset.py`
- ✅ Crea nuevo período con `PeriodService`
- ✅ Valida reseteo completo de usuarios
- ✅ Valida creación de registros en `user_rank_history`

**Resultado:**
```
✅ 1023 usuarios reiniciados
✅ 1023 registros de rango creados (rank_id=1)
✅ TODAS LAS PRUEBAS PASARON
```

### 2. `test_admin_period_creation.py`
- ✅ Simula creación de período desde Admin Panel
- ✅ Valida reseteo completo de usuarios
- ✅ Valida creación de registros en `user_rank_history`

**Resultado:**
```
✅ 1023 usuarios reiniciados
✅ 1023 registros de rango creados (rank_id=1)
✅ TEST DE ADMIN PANEL COMPLETADO
```

### 3. `test_no_reset_existing_period.py`
- ✅ Valida que NO se resetea si el período ya existe
- ✅ Usuarios mantienen sus valores
- ✅ No se duplican registros de `user_rank_history`

**Resultado:**
```
✅ Se retornó el período existente (correcto)
✅ Usuarios mantienen sus valores (correcto)
✅ Registros sin duplicar (correcto)
```

## 📊 Flujo de Ejecución

```
┌─────────────────────────────────────┐
│  Crear Nuevo Período                │
│  (cualquier método)                 │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  ¿Período ya existe?                │
└─────────────┬───────────────────────┘
              │
        ┌─────┴─────┐
        │           │
       SÍ          NO
        │           │
        ▼           ▼
┌──────────┐  ┌──────────────────────┐
│ Retornar │  │ 1. Crear período     │
│ existente│  │ 2. Resetear usuarios │
│          │  │ 3. Crear rank history│
└──────────┘  └──────────────────────┘
```

## 🎯 Casos de Uso

### Caso 1: Cierre de Mes Automático
```python
# Scheduler ejecuta cierre automático
PeriodService.check_and_manage_periods(session)
# ✅ Resetea usuarios automáticamente
```

### Caso 2: Cierre Manual desde Admin
```python
# Admin cierra período y crea nuevo
# ✅ Resetea usuarios automáticamente
```

### Caso 3: Creación de Período Específico
```python
# Crear período de diciembre 2025
PeriodService.create_period_for_month(session, 2025, 12)
# ✅ Resetea usuarios automáticamente
```

## 🔒 Garantías de Seguridad

1. **Transaccionalidad**: Todo ocurre en una transacción (rollback automático en error)
2. **Sin duplicación**: Si el período existe, no se resetea
3. **Consistencia**: Todos los usuarios se resetean o ninguno
4. **Trazabilidad**: Logs detallados de cada operación

## 📝 Logs Esperados

```
✅ Período creado: 2025-11 (2025-11-01 - 2025-11-30)

🔄 Reiniciando usuarios para período 2025-11...
   ✅ 1023 usuarios reiniciados
   ✅ 1023 registros de rango creados (rank_id=1)
```

## ⚠️ Consideraciones Importantes

1. **No es reversible**: Una vez reseteado, no se puede deshacer
2. **Todos los usuarios**: El reset afecta a TODOS los usuarios
3. **Automático**: No requiere intervención manual
4. **Independiente del método**: Funciona igual sin importar cómo se cree el período

## 🚀 Ventajas de esta Implementación

1. ✅ **Centralizada**: Un solo método, fácil de mantener
2. ✅ **Automática**: No se puede olvidar ejecutar el reset
3. ✅ **Consistente**: Comportamiento idéntico en todos los flujos
4. ✅ **Segura**: Manejo de errores y transacciones
5. ✅ **Testeable**: Tests completos validan todos los casos
6. ✅ **Documentada**: Código con comentarios claros

## 📚 Archivos Modificados

1. `NNProtect_new_website/mlm_service/period_service.py`
   - Agregado: `reset_users_for_new_period()`
   - Modificado: `create_period_for_month()`

2. `NNProtect_new_website/Admin_app/admin_state.py`
   - Modificado: Función de cierre de período

3. Tests creados:
   - `test_period_reset.py`
   - `test_admin_period_creation.py`
   - `test_no_reset_existing_period.py`

---

**Fecha de implementación**: 30 de octubre de 2025
**Versión**: 1.0
**Estado**: ✅ Implementado y validado
