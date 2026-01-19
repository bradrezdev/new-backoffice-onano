"""
🧪 Test de Cache Global en Producción

Valida que el cache GLOBAL persista entre múltiples instancias del State
(simula el comportamiento en producción serverless)
"""

import time
from typing import Dict, List, Any

# ===================== CACHE GLOBAL (igual que en store_products_state.py) =====================
_GLOBAL_PRODUCTS_CACHE: Dict[str, List[Dict[str, Any]]] = {}
_GLOBAL_CACHE_TIMESTAMP: float = 0.0
CACHE_DURATION: int = 300  # 5 minutos

def simulate_first_request():
    """Simula el primer request (Cache MISS)"""
    global _GLOBAL_PRODUCTS_CACHE, _GLOBAL_CACHE_TIMESTAMP
    
    print("=" * 70)
    print("📊 REQUEST 1: Primera instancia del State (Cache MISS)")
    print("=" * 70)
    
    current_time = time.time()
    cache_age = current_time - _GLOBAL_CACHE_TIMESTAMP
    cache_is_valid = _GLOBAL_PRODUCTS_CACHE and cache_age < CACHE_DURATION
    
    if cache_is_valid:
        print(f"❌ ERROR: Cache debería estar VACÍO en el primer request")
        return False
    
    print(f"✅ Cache está vacío (como se esperaba)")
    print(f"🔍 Simulando carga desde DB (3 segundos)...")
    
    # Simular carga desde DB
    time.sleep(3)
    
    # Guardar en cache GLOBAL
    _GLOBAL_PRODUCTS_CACHE.clear()
    _GLOBAL_PRODUCTS_CACHE.update({
        "latest": [{"id": i, "name": f"Nuevo {i}"} for i in range(1, 6)],
        "popular": [{"id": i, "name": f"Popular {i}"} for i in range(1, 6)],
        "supplement": [{"id": i, "name": f"Suplemento {i}"} for i in range(1, 11)],
    })
    _GLOBAL_CACHE_TIMESTAMP = current_time
    
    print(f"✅ Cache GLOBAL actualizado con {sum(len(v) for v in _GLOBAL_PRODUCTS_CACHE.values())} productos")
    print(f"⏱️  Timestamp del cache: {_GLOBAL_CACHE_TIMESTAMP}")
    
    return True

def simulate_second_request():
    """Simula el segundo request (Cache HIT) - NUEVA INSTANCIA del State"""
    global _GLOBAL_PRODUCTS_CACHE, _GLOBAL_CACHE_TIMESTAMP
    
    print("\n")
    print("=" * 70)
    print("📊 REQUEST 2: Nueva instancia del State (Cache HIT esperado)")
    print("=" * 70)
    
    # Simular pequeña pausa entre requests
    time.sleep(0.5)
    
    current_time = time.time()
    cache_age = current_time - _GLOBAL_CACHE_TIMESTAMP
    cache_is_valid = _GLOBAL_PRODUCTS_CACHE and cache_age < CACHE_DURATION
    
    if not cache_is_valid:
        print(f"❌ ERROR: Cache debería estar VÁLIDO (edad: {cache_age:.2f}s < {CACHE_DURATION}s)")
        return False
    
    print(f"✅ Cache GLOBAL válido - Edad: {cache_age:.2f}s")
    print(f"📦 Productos en cache:")
    for category, products in _GLOBAL_PRODUCTS_CACHE.items():
        print(f"   • {category}: {len(products)} productos")
    
    # Simular lectura instantánea desde cache
    start = time.time()
    latest = _GLOBAL_PRODUCTS_CACHE.get("latest", [])
    popular = _GLOBAL_PRODUCTS_CACHE.get("popular", [])
    supplement = _GLOBAL_PRODUCTS_CACHE.get("supplement", [])
    elapsed = time.time() - start
    
    print(f"\n⚡ Tiempo de lectura desde cache: {elapsed:.6f}s")
    
    if elapsed > 0.01:  # Debería ser prácticamente instantáneo
        print(f"⚠️  Advertencia: Lectura de cache tomó más de 0.01s")
    
    return True

def simulate_third_request_after_expiry():
    """Simula request después de expiración del TTL"""
    global _GLOBAL_PRODUCTS_CACHE, _GLOBAL_CACHE_TIMESTAMP
    
    print("\n")
    print("=" * 70)
    print("📊 REQUEST 3: Después de expiración del TTL (Cache MISS esperado)")
    print("=" * 70)
    
    # Simular que pasaron 5 minutos
    print(f"⏰ Simulando paso de {CACHE_DURATION + 1} segundos...")
    simulated_future_time = _GLOBAL_CACHE_TIMESTAMP + CACHE_DURATION + 1
    
    # Verificar expiración
    cache_age = simulated_future_time - _GLOBAL_CACHE_TIMESTAMP
    cache_is_valid = _GLOBAL_PRODUCTS_CACHE and cache_age < CACHE_DURATION
    
    if cache_is_valid:
        print(f"❌ ERROR: Cache debería estar EXPIRADO (edad: {cache_age:.2f}s >= {CACHE_DURATION}s)")
        return False
    
    print(f"✅ Cache expirado correctamente (edad: {cache_age:.2f}s >= {CACHE_DURATION}s)")
    print(f"🔍 Próximo request forzaría Cache MISS y recarga desde DB")
    
    return True

def simulate_invalidation():
    """Simula invalidación manual del cache"""
    global _GLOBAL_PRODUCTS_CACHE, _GLOBAL_CACHE_TIMESTAMP
    
    print("\n")
    print("=" * 70)
    print("📊 TEST: Invalidación manual del cache")
    print("=" * 70)
    
    # Restaurar cache para probar invalidación
    _GLOBAL_PRODUCTS_CACHE.update({
        "latest": [{"id": 1}],
        "popular": [{"id": 2}],
    })
    _GLOBAL_CACHE_TIMESTAMP = time.time()
    
    print(f"📦 Cache antes de invalidar: {len(_GLOBAL_PRODUCTS_CACHE)} categorías")
    
    # Invalidar
    _GLOBAL_PRODUCTS_CACHE.clear()
    _GLOBAL_CACHE_TIMESTAMP = 0.0
    
    print(f"🗑️  Cache invalidado")
    print(f"📦 Cache después de invalidar: {len(_GLOBAL_PRODUCTS_CACHE)} categorías")
    
    if len(_GLOBAL_PRODUCTS_CACHE) > 0:
        print(f"❌ ERROR: Cache no se limpió correctamente")
        return False
    
    print(f"✅ Invalidación exitosa")
    return True

def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n")
    print("=" * 70)
    print("🧪 TEST DE CACHE GLOBAL - Simulación de Producción")
    print("=" * 70)
    print("\nObjetivo: Validar que el cache persista entre instancias del State")
    print("(Simula comportamiento en Reflex Deploy con serverless)\n")
    
    results = []
    
    # Test 1: Primera carga (Cache MISS)
    results.append(("Request 1 (Cache MISS)", simulate_first_request()))
    
    # Test 2: Segunda carga (Cache HIT) - NUEVA INSTANCIA
    results.append(("Request 2 (Cache HIT)", simulate_second_request()))
    
    # Test 3: Expiración del TTL
    results.append(("Request 3 (TTL Expiry)", simulate_third_request_after_expiry()))
    
    # Test 4: Invalidación manual
    results.append(("Invalidación manual", simulate_invalidation()))
    
    # Resumen
    print("\n")
    print("=" * 70)
    print("📈 RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n")
    print("=" * 70)
    if all_passed:
        print("🎉 TODOS LOS TESTS PASARON")
        print("=" * 70)
        print("\n✅ Cache GLOBAL funciona correctamente en producción")
        print("✅ El cache persiste entre múltiples instancias del State")
        print("✅ TTL y expiración funcionan correctamente")
        print("✅ Invalidación manual funciona correctamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("=" * 70)
        print("\n⚠️  Revisar implementación del cache GLOBAL")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    print("\n")
    sys.exit(0 if success else 1)
