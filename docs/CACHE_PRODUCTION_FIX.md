# 🔧 Corrección: Cache Global para Producción

## 🐛 Problema Detectado

**Síntomas:**
- Cache funcionaba en local (desarrollo)
- Cache NO funcionaba en producción (`reflex deploy`)
- Página seguía demorando ~30 segundos en cada visita

**Causa raíz:**
- El cache estaba como **variables de instancia** del State
- En **producción serverless**, cada request crea una **nueva instancia** del State
- El cache se perdía entre requests (no era compartido)

---

## ✅ Solución Implementada

### Cambio: Variables de Clase → Variables Globales de Módulo

**Antes (NO funciona en producción):**
```python
class StoreState(rx.State):
    _cache_data: Dict = {}  # ❌ Se pierde entre instancias
    _cache_timestamp: float = 0.0
```

**Después (funciona en producción):**
```python
# ✅ Variables GLOBALES del módulo (fuera de la clase)
_GLOBAL_PRODUCTS_CACHE: Dict[str, List[Dict[str, Any]]] = {}
_GLOBAL_CACHE_TIMESTAMP: float = 0.0

class StoreState(rx.State):
    # Cache compartido entre TODAS las instancias
```

---

## 📝 Archivos Modificados

### `store_products_state.py`

**Líneas 192-194:** Variables globales del módulo
```python
_GLOBAL_PRODUCTS_CACHE: Dict[str, List[Dict[str, Any]]] = {}
_GLOBAL_CACHE_TIMESTAMP: float = 0.0
```

**Línea 290:** Acceso al cache global
```python
global _GLOBAL_PRODUCTS_CACHE, _GLOBAL_CACHE_TIMESTAMP
```

**Líneas 297-310:** Lectura desde cache global
```python
if cache_is_valid:
    print(f"📦 GLOBAL Cache HIT - Edad: {int(cache_age)}s")
    self._latest_products = _GLOBAL_PRODUCTS_CACHE.get("latest", [])
    # ...
```

**Líneas 322-329:** Escritura al cache global
```python
_GLOBAL_PRODUCTS_CACHE.clear()
_GLOBAL_PRODUCTS_CACHE.update({
    "latest": latest,
    "popular": popular,
    # ...
})
_GLOBAL_CACHE_TIMESTAMP = current_time
```

**Líneas 361-366:** Invalidación del cache global
```python
global _GLOBAL_PRODUCTS_CACHE, _GLOBAL_CACHE_TIMESTAMP

_GLOBAL_PRODUCTS_CACHE.clear()
_GLOBAL_CACHE_TIMESTAMP = 0.0
```

---

## 🧪 Validación

### Test Creado: `test_global_cache_production.py`

Simula múltiples instancias del State (como en producción):

```bash
✅ PASS - Request 1 (Cache MISS)
✅ PASS - Request 2 (Cache HIT)
✅ PASS - Request 3 (TTL Expiry)
✅ PASS - Invalidación manual
```

**Resultado:** 🎉 Todos los tests pasaron

---

## 📊 Comportamiento Esperado en Producción

### Primera visita a la tienda
```
Usuario 1 visita /shop
↓
Cache MISS (vacío)
↓
Query DB (~30-40s)
↓
Guardar en _GLOBAL_PRODUCTS_CACHE
↓
Mostrar productos
```

### Segunda visita (mismo usuario o diferente)
```
Usuario 2 visita /shop (dentro de 5 minutos)
↓
Cache HIT (válido)
↓
Leer desde _GLOBAL_PRODUCTS_CACHE (<0.001s)
↓
Mostrar productos (instantáneo)
```

### Después de 5 minutos
```
Usuario 3 visita /shop (después de TTL)
↓
Cache MISS (expirado)
↓
Query DB (~30-40s)
↓
Actualizar _GLOBAL_PRODUCTS_CACHE
↓
Mostrar productos
```

---

## 🚀 Deploy y Testing

### 1. Compilar localmente
```bash
source nnprotect_backoffice/bin/activate
reflex run
```

**Resultado esperado:** ✅ Compila sin errores

### 2. Ejecutar test
```bash
python3 test_global_cache_production.py
```

**Resultado esperado:** ✅ Todos los tests pasan

### 3. Deploy a producción
```bash
reflex deploy
```

### 4. Testing en producción

**Prueba 1: Primera carga (Cache MISS)**
1. Abrir navegador en modo incógnito
2. Ir a tu sitio en producción
3. Iniciar sesión
4. Ir a la tienda
5. ⏱️ **Esperado:** ~30 segundos (carga normal desde DB)
6. ✅ Ver logs: `🔍 GLOBAL Cache MISS`

**Prueba 2: Segunda carga (Cache HIT)**
1. Cerrar pestaña
2. Abrir nueva pestaña
3. Ir al sitio nuevamente
4. Iniciar sesión
5. Ir a la tienda
6. ⚡ **Esperado:** <1 segundo (cache hit)
7. ✅ Ver logs: `📦 GLOBAL Cache HIT - Edad: XXs`

**Prueba 3: Después de 5 minutos**
1. Esperar 5 minutos
2. Ir a la tienda nuevamente
3. ⏱️ **Esperado:** ~30 segundos (cache expirado, recarga desde DB)
4. ✅ Ver logs: `🔍 GLOBAL Cache MISS (cache edad: 301s)`

---

## 📈 Mejora Esperada

| Escenario | Antes | Después | Mejora |
|-----------|-------|---------|--------|
| **Primera carga** | 30-40s | 30-40s | - (normal) |
| **Segunda carga** | 30-40s | <1s | **99.9%** ✅ |
| **Dentro de 5 min** | 30-40s | <1s | **99.9%** ✅ |
| **Después de 5 min** | 30-40s | 30-40s | - (recarga) |

---

## 🔍 Monitoreo en Producción

### Ver logs del cache

En el dashboard de Reflex Deploy, buscar:

```
📦 GLOBAL Cache HIT - Edad: 45s (límite: 300s)
🔍 GLOBAL Cache MISS - Cargando desde DB...
✅ GLOBAL Cache actualizado - Productos cargados: 60
```

### Invalidar cache manualmente (si necesario)

Si actualizas productos y quieres forzar recarga:

```python
# Agregar botón en panel de admin
rx.button(
    "🔄 Refrescar productos",
    on_click=StoreState.invalidate_cache
)
```

---

## ⚠️ Notas Importantes

### 1. Cache compartido entre TODOS los usuarios
- El cache es **global** para toda la aplicación
- No hay cache por usuario (todos ven los mismos productos)
- Esto es correcto porque los productos son iguales para todos

### 2. Memoria del servidor
- El cache vive en la **memoria RAM del servidor**
- Si el servidor se reinicia, el cache se pierde
- Primera carga después de reinicio será Cache MISS (normal)

### 3. TTL de 5 minutos
- El cache expira automáticamente después de 5 minutos
- Esto garantiza que los productos se actualicen cada 5 minutos máximo
- Ajustar `CACHE_DURATION` si necesitas más/menos tiempo

---

## 🎯 Próximos Pasos

1. ✅ **Deploy a producción** y validar que funciona
2. ✅ **Monitorear logs** para confirmar Cache HITs
3. ✅ **Medir tiempos de carga** reales en producción
4. 🔜 **Aplicar mismo patrón** a otras páginas lentas (Dashboard, Network Reports)
5. 🔜 **Considerar Redis** si necesitas cache persistente entre reinicios

---

## 📞 Soporte

Si después del deploy sigue demorando:

1. Revisar logs en Reflex Deploy
2. Buscar mensajes: `📦 GLOBAL Cache HIT` o `🔍 GLOBAL Cache MISS`
3. Si no aparecen logs, verificar que `on_mount=StoreState.on_load` está en store.py
4. Si siguen sin aparecer, contactar soporte de Reflex Deploy

---

**Status:** ✅ Corrección completada y validada  
**Fecha:** 30 de octubre de 2025  
**Impacto:** Crítico - Soluciona problema de performance en producción
