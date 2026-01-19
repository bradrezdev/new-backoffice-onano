#!/usr/bin/env python3
"""
INSTRUCCIONES: Cómo usar el sistema de recálculo automático de comisiones

El dashboard ahora recalcula automáticamente las ganancias estimadas cada vez
que los PVG del usuario cambian, sin importar cuánto sea el cambio.

═══════════════════════════════════════════════════════════════════════════════
ARQUITECTURA IMPLEMENTADA
═══════════════════════════════════════════════════════════════════════════════

1. ✅ DETECCIÓN AUTOMÁTICA DE CAMBIOS
   - `load_rank_progression()` ahora detecta cambios en `current_pvg`
   - Si el PVG cambió (de cualquier valor a cualquier otro valor), dispara automáticamente
     `load_estimated_monthly_earnings()`
   - No importa si el cambio es de 0→1, 293→293.1, o cualquier otro

2. ✅ MÉTODO PÚBLICO PARA REFRESCAR
   - Nuevo método: `DashboardState.refresh_dashboard_data()`
   - Este método recarga TODOS los datos del dashboard:
     * Progresión de rango (PVG actual, siguiente rango, porcentaje)
     * Ganancias estimadas (comisiones calculadas del período)
   - Debe llamarse después de cualquier operación que modifique los PVG

3. ✅ PRINCIPIO REACTIVO
   - El sistema responde automáticamente a cambios de datos
   - No requiere intervención manual
   - Mantiene la UI sincronizada con la base de datos

═══════════════════════════════════════════════════════════════════════════════
CASOS DE USO
═══════════════════════════════════════════════════════════════════════════════

CASO 1: Después de crear una orden (Admin App)
-------------------------------------------------
Ubicación: Admin_app/admin_state.py - método create_orders()

# ❌ ANTES (No refrescaba el dashboard)
session.commit()
return rx.toast.success("Órdenes creadas exitosamente")

# ✅ AHORA (Refresca automáticamente)
session.commit()

# Obtener el DashboardState y refrescar
from ..NNProtect_new_website import DashboardState
dashboard_state = await self.get_state(DashboardState)
await dashboard_state.refresh_dashboard_data()

return rx.toast.success("Órdenes creadas y dashboard actualizado")


CASO 2: Después de confirmar pago de una orden
------------------------------------------------
Ubicación: order_service/order_state.py (si existe)

# Después de actualizar PVG en la base de datos
session.commit()

# Refrescar dashboard
from ..NNProtect_new_website import DashboardState
dashboard_state = await self.get_state(DashboardState)
await dashboard_state.refresh_dashboard_data()


CASO 3: Después de reset de período
-------------------------------------
Ubicación: Admin_app/admin_state.py - método process_period_end_and_commissions()

# Después de resetear usuarios (PVG vuelve a 0)
PeriodResetService.reset_all_users_for_new_period(session, new_period.id)
session.commit()

# Refrescar dashboard
from ..NNProtect_new_website import DashboardState
dashboard_state = await self.get_state(DashboardState)
await dashboard_state.refresh_dashboard_data()


CASO 4: En tiempo real durante navegación del usuario
-------------------------------------------------------
El usuario no necesita hacer nada. Cuando carga el dashboard:

on_mount=[
    AuthState.load_user_from_token,
    DashboardState.load_user_stats,
    DashboardState.load_rank_progression,  # ← Esto detecta cambios automáticamente
    DashboardState.load_estimated_monthly_earnings,
]

Si el PVG cambió desde la última vez, se recalcula automáticamente.


═══════════════════════════════════════════════════════════════════════════════
INTEGRACIÓN CON PVUpdateService
═══════════════════════════════════════════════════════════════════════════════

Si estás usando PVUpdateService para actualizar PVG:

Ubicación: mlm_service/pv_update_service.py

@classmethod
def process_order_pv_update(cls, session, order_id: int) -> bool:
    # ... (código existente que actualiza PVG) ...
    
    session.commit()
    
    # ✅ AGREGAR: Notificar al dashboard que debe refrescarse
    # Nota: Esto requiere que el método sea async o que uses un event bus
    # Por ahora, el dashboard se refresca cuando el usuario recarga la página
    
    return True

ALTERNATIVA RECOMENDADA (Patrón Event-Driven):
------------------------------------------------
Crear un sistema de eventos para notificar cambios de PVG:

# En un nuevo archivo: events/pvg_events.py
class PVGUpdateEvent:
    @staticmethod
    async def on_pvg_changed(member_id: int):
        \"\"\"Dispara refresco del dashboard cuando PVG cambia\"\"\"
        # Obtener el DashboardState del usuario
        # Llamar a refresh_dashboard_data()
        pass

# Luego, en cualquier lugar que modifique PVG:
await PVGUpdateEvent.on_pvg_changed(member_id)


═══════════════════════════════════════════════════════════════════════════════
TESTING
═══════════════════════════════════════════════════════════════════════════════

Para probar el sistema de recálculo automático:

1. Abrir el dashboard del usuario (member_id=1)
2. Verificar la proyección de ganancias actual
3. Crear una orden desde Admin App
4. Volver al dashboard y recargar la página
5. Verificar que la proyección se actualizó automáticamente

Script de prueba:
-----------------
python test_rank_and_earnings_fixes.py

Este script verifica:
- ✅ Rango actual viene del período actual
- ✅ Máximo rango viene de toda la vida
- ✅ Ganancias = $0 cuando PVG = 0
- ✅ Ganancias se actualizan cuando PVG > 0


═══════════════════════════════════════════════════════════════════════════════
NOTAS TÉCNICAS
═══════════════════════════════════════════════════════════════════════════════

1. PERFORMANCE
   - El recálculo solo ocurre cuando PVG cambia (no en cada render)
   - Las queries están optimizadas con índices en pvg_cache y period_id
   - El cálculo es simple: suma de comisiones del período (no recalcula todo)

2. LIMITACIONES ACTUALES
   - El refresco automático solo funciona cuando el usuario recarga el dashboard
   - No hay WebSocket para actualización en tiempo real
   - Si otro usuario modifica el PVG, el dashboard no se actualiza hasta reload

3. MEJORAS FUTURAS POSIBLES
   - Implementar WebSocket para push de actualizaciones en tiempo real
   - Agregar un polling interval (cada 30 segundos verificar cambios)
   - Implementar un event bus centralizado para notificaciones

═══════════════════════════════════════════════════════════════════════════════

Arquitectura: Adrian (KISS + Reactivo) + Giovanni (QA + Testing)
Fecha: 2025-01-30
"""

print(__doc__)
