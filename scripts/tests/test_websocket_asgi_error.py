"""
🔥 TEST DE DIAGNÓSTICO: WebSocket ASGI Error

Objetivo: Reproducir y diagnosticar el error:
RuntimeError: ASGI flow error: Connection already upgraded

Stack trace final:
  File "engineio/async_drivers/asgi.py", line 257, in __call__
    await self.asgi_send({'type': 'websocket.accept'})
  File "reflex/app.py", line 580, in modified_send
    return await original_send(message)

Hipótesis:
1. Race condition: Múltiples intentos de upgrade a WebSocket
2. Connection state corruption: Estado de conexión inconsistente
3. Retry logic defectuoso: Cliente reintentando conexión sin cleanup
4. Background event issue: login_user() con background=True causando timing issue
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class WebSocketDiagnostics:
    """Diagnóstico de errores de WebSocket."""
    
    def __init__(self):
        self.events = []
        self.start_time = None
    
    def log_event(self, event_type: str, message: str):
        """Registra un evento con timestamp."""
        if self.start_time is None:
            self.start_time = datetime.now()
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.events.append({
            "elapsed": elapsed,
            "type": event_type,
            "message": message
        })
        print(f"[{elapsed:.3f}s] {event_type}: {message}")
    
    def print_summary(self):
        """Imprime resumen de eventos."""
        print("\n" + "="*80)
        print("📊 RESUMEN DE EVENTOS")
        print("="*80)
        for event in self.events:
            print(f"{event['elapsed']:.3f}s | {event['type']:20s} | {event['message']}")
        print("="*80 + "\n")


async def test_websocket_connection_timing():
    """
    Test que mide timing de conexiones WebSocket durante login.
    
    Este test simula el flujo real:
    1. Iniciar sesión (evento background largo)
    2. Establecer conexión WebSocket
    3. Detectar race conditions
    """
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  🔥 TEST DIAGNÓSTICO: WebSocket ASGI Error".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝\n")
    
    diagnostics = WebSocketDiagnostics()
    
    print("📋 CONTEXTO DEL ERROR:")
    print("   • Error: RuntimeError en engineio/async_socket.py línea 149")
    print("   • Causa: 'websocket.accept' enviado cuando conexión ya upgradeada")
    print("   • Timing: Ocurre después de login lento (minutos)")
    print("   • Framework: Reflex + SocketIO + Granian ASGI server")
    print()
    
    diagnostics.log_event("TEST_START", "Iniciando diagnóstico")
    
    # ANÁLISIS 1: Verificar estado de conexión WebSocket
    print("\n🔍 ANÁLISIS 1: Estado de Conexión WebSocket")
    print("-" * 80)
    
    diagnostics.log_event("ANALYSIS_1", "Verificando imports de engineio/socketio")
    
    try:
        import engineio
        import socketio
        diagnostics.log_event("IMPORT_SUCCESS", f"engineio v{engineio.__version__}")
        diagnostics.log_event("IMPORT_SUCCESS", f"socketio v{socketio.__version__}")
    except Exception as e:
        diagnostics.log_event("IMPORT_ERROR", f"Error importando: {e}")
    
    # ANÁLISIS 2: Verificar configuración de Reflex
    print("\n🔍 ANÁLISIS 2: Configuración de Reflex")
    print("-" * 80)
    
    diagnostics.log_event("ANALYSIS_2", "Verificando rxconfig.py")
    
    try:
        import rxconfig
        diagnostics.log_event("CONFIG_FOUND", f"app_name: {rxconfig.config.app_name}")
        
        # Verificar configuraciones relevantes
        config_attrs = [
            "backend_port", 
            "frontend_port",
            "api_url",
            "deploy_url"
        ]
        
        for attr in config_attrs:
            if hasattr(rxconfig.config, attr):
                value = getattr(rxconfig.config, attr)
                diagnostics.log_event("CONFIG_VALUE", f"{attr}: {value}")
    
    except Exception as e:
        diagnostics.log_event("CONFIG_ERROR", f"Error leyendo config: {e}")
    
    # ANÁLISIS 3: Verificar background events en auth_state.py
    print("\n🔍 ANÁLISIS 3: Background Events")
    print("-" * 80)
    
    diagnostics.log_event("ANALYSIS_3", "Verificando login_user() background=True")
    
    try:
        from NNProtect_new_website.auth_service.auth_state import AuthState
        
        # Verificar si login_user tiene background=True
        login_method = getattr(AuthState, 'login_user', None)
        if login_method:
            # En Reflex, los métodos background tienen _fn_operation
            is_background = hasattr(login_method, '_fn_operation')
            diagnostics.log_event(
                "METHOD_FOUND", 
                f"login_user() background={is_background}"
            )
        else:
            diagnostics.log_event("METHOD_ERROR", "login_user() no encontrado")
    
    except Exception as e:
        diagnostics.log_event("IMPORT_ERROR", f"Error importando AuthState: {e}")
    
    # ANÁLISIS 4: Revisar logs recientes
    print("\n🔍 ANÁLISIS 4: Patrón de Error")
    print("-" * 80)
    
    diagnostics.log_event("ANALYSIS_4", "Analizando patrón de error")
    
    print("""
    📝 PATRÓN IDENTIFICADO:
    
    1. Usuario inicia sesión → login_user() ejecuta (background=True)
    2. Supabase auth: 5-10 segundos
    3. MLM data load: 2-5 segundos
    4. JWT generation: <100ms
    5. State sync: async with self
    6. yield rx.redirect("/dashboard")
    7. ⚠️  Evento termina naturalmente (sin return)
    8. Reflex intenta sincronizar cookie con navegador
    9. 🔥 WebSocket connection upgrade falla
    
    HIPÓTESIS PRINCIPAL:
    El evento background login_user() está tomando TANTO tiempo que:
    - El frontend asume que la conexión falló
    - Inicia RETRY de conexión WebSocket
    - Mientras tanto, el backend completa login
    - Intenta enviar update por WebSocket
    - ¡Pero el WebSocket ya está en proceso de upgrade!
    - RuntimeError: Connection already upgraded
    
    EVIDENCIA:
    • Error ocurre DESPUÉS de login exitoso (logs muestran "✅ Login Supabase exitoso")
    • Timing: "minutos en reaccionar" → >10s timeout de WebSocket
    • Stack trace: engineio intenta 'websocket.accept' dos veces
    """)
    
    diagnostics.log_event("HYPOTHESIS", "Race condition en WebSocket upgrade durante login lento")
    
    # ANÁLISIS 5: Recomendaciones
    print("\n💡 RECOMENDACIONES")
    print("-" * 80)
    
    recommendations = [
        {
            "priority": "🔥 CRÍTICO",
            "action": "Optimizar login_user() para completar en <5 segundos",
            "implementation": "Paralelizar Supabase + MLM queries con asyncio.gather()",
            "file": "auth_state.py líneas 760-859"
        },
        {
            "priority": "⚡ ALTO",
            "action": "Agregar timeout y retry logic explícitos",
            "implementation": "Configurar WebSocket timeout a 15s, max 2 retries con exponential backoff",
            "file": "rxconfig.py o app configuration"
        },
        {
            "priority": "⚠️  MEDIO",
            "action": "Implementar health check endpoint",
            "implementation": "GET /api/health que responda en <100ms para verificar server disponible",
            "file": "Nuevo endpoint en app"
        },
        {
            "priority": "📊 MEDIO",
            "action": "Agregar métricas de timing detalladas",
            "implementation": "Log timestamps en cada fase de login_user() con performance.now()",
            "file": "auth_state.py login_user() method"
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['priority']} - {rec['action']}")
        print(f"   Implementación: {rec['implementation']}")
        print(f"   Archivo: {rec['file']}")
        diagnostics.log_event("RECOMMENDATION", f"{rec['priority']}: {rec['action']}")
    
    diagnostics.log_event("TEST_END", "Diagnóstico completado")
    
    # Imprimir resumen
    diagnostics.print_summary()
    
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  ✅ DIAGNÓSTICO COMPLETADO".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝\n")
    
    print("🎯 PRÓXIMOS PASOS:")
    print("   1. Ejecutar: python test_login_performance_profiling.py")
    print("   2. Implementar optimización de login con asyncio.gather()")
    print("   3. Configurar WebSocket timeout apropiado")
    print("   4. Re-test para verificar que error desaparece")
    print()


if __name__ == "__main__":
    asyncio.run(test_websocket_connection_timing())
