"""
Utilidades de autenticación y protección de rutas.
"""
import reflex as rx
from NNProtect_new_website.modules.auth.state.auth_state import AuthState

def require_auth(page_component):
    """
    Decorador para proteger rutas.
    Envuelve una página y agrega la verificación de autenticación al cargar.
    
    Uso:
    @require_auth
    def my_page():
        return rx.vstack(...)
        
    O en la definición de rutas:
    app.add_page(require_auth(dashboard), ...)
    """
    def wrapper(*args, **kwargs):
        component = page_component(*args, **kwargs)
        
        # Agregar el evento on_mount para verificar login
        # Si el componente ya tiene on_mount, lo preservamos (si es posible en Reflex API futura)
        # Por ahora, Reflex permite una lista de eventos en on_mount.
        
        # Nota: En Reflex, on_mount puede ser un evento o una lista.
        # Introspección del componente (esto varía según versión de Reflex)
        
        # Estrategia más segura: Retornar un Fragment que envuelva y tenga el on_mount
        return rx.fragment(
            component,
            on_mount=AuthState.ensure_logged_in
        )
    
    return wrapper

def require_guest(page_component):
    """
    Decorador para proteger rutas 'GUEST ONLY' (como Login).
    Si el usuario ya está autenticado, redirige al dashboard.
    """
    def wrapper(*args, **kwargs):
        component = page_component(*args, **kwargs)
        return rx.fragment(
            component,
            on_mount=AuthState.ensure_not_logged_in
        )
    return wrapper
