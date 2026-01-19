"""
Manager especializado para operaciones de Supabase Auth.
Implementa autenticación basada en contraseñas según documentación oficial.
Referencia: https://supabase.com/docs/guides/auth/passwords?language=python
"""

from typing import Optional, Dict, Any, Tuple
from .supabase_client import supabase
import asyncio

class SupabaseAuthManager:
    """Maneja todas las operaciones de Supabase Auth según documentación oficial."""
    
    @staticmethod
    async def sign_up_user(email: str, password: str, display_name: str, 
                          first_name: str, last_name: str) -> Tuple[bool, str, Optional[str]]:
        """
        Registra usuario en Supabase Auth con metadata adicional.
        Implementación según: https://supabase.com/docs/guides/auth/passwords?language=python
        
        Returns: (success, message, user_id)
        """
        try:
            # Según la documentación oficial de Supabase
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "display_name": display_name,
                        "first_name": first_name,
                        "last_name": last_name
                    }
                }
            })
            
            if response.user:
                print(f"✅ Usuario registrado en Supabase: {email}")
                return True, "Usuario creado exitosamente", response.user.id
            else:
                return False, "Error creando usuario en Supabase", None
                
        except Exception as e:
            error_msg = str(e).lower()
            print(f"❌ Error Supabase signup: {e}")
            
            if "user already registered" in error_msg or "already been registered" in error_msg:
                return False, "El email ya está registrado", None
            elif "password" in error_msg:
                return False, "La contraseña no cumple con los requisitos", None
            elif "email" in error_msg:
                return False, "Email inválido", None
            
            return False, f"Error de registro: {str(e)}", None

    @staticmethod
    async def sign_in_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Inicia sesión en Supabase Auth.
        Implementación según documentación oficial.
        
        Returns: (success, message, user_data)
        """
        try:
            # Según la documentación oficial de Supabase
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                user_data = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "display_name": response.user.user_metadata.get("display_name", ""),
                    "first_name": response.user.user_metadata.get("first_name", ""),
                    "last_name": response.user.user_metadata.get("last_name", ""),
                    "created_at": response.user.created_at,
                    "access_token": response.session.access_token if response.session else None,
                }
                print(f"✅ Login Supabase exitoso: {email}")
                return True, "Login exitoso", user_data
            else:
                return False, "Credenciales inválidas", None
                
        except Exception as e:
            error_msg = str(e).lower()
            print(f"❌ Error Supabase login: {e}")
            
            if "invalid login credentials" in error_msg or "invalid" in error_msg:
                return False, "Email o contraseña incorrectos", None
            elif "email not confirmed" in error_msg:
                return False, "Por favor confirma tu email antes de iniciar sesión", None
            
            return False, f"Error de login: {str(e)}", None

    @staticmethod
    def sign_out_user() -> bool:
        """Cierra sesión en Supabase según documentación oficial."""
        try:
            supabase.auth.sign_out()
            print("✅ Logout Supabase exitoso")
            return True
        except Exception as e:
            print(f"❌ Error logout Supabase: {e}")
            return False

    @staticmethod
    def get_current_session() -> Optional[Dict[str, Any]]:
        """
        Obtiene la sesión actual de Supabase.
        Implementación según documentación oficial.
        """
        try:
            session = supabase.auth.get_session()
            if session and session.user:
                return {
                    "user_id": session.user.id,
                    "email": session.user.email,
                    "display_name": session.user.user_metadata.get("display_name", ""),
                    "first_name": session.user.user_metadata.get("first_name", ""),
                    "last_name": session.user.user_metadata.get("last_name", ""),
                    "access_token": session.access_token,
                    "expires_at": session.expires_at,
                }
            return None
        except Exception as e:
            print(f"❌ Error obteniendo sesión Supabase: {e}")
            return None

    @staticmethod
    async def reset_password(email: str) -> Tuple[bool, str]:
        """Envía email de reset de contraseña según documentación oficial."""
        try:
            supabase.auth.reset_password_email(email)
            return True, "Email de recuperación enviado"
        except Exception as e:
            return False, f"Error enviando email: {str(e)}"

    @staticmethod
    def get_user_metadata() -> Optional[Dict[str, Any]]:
        """Obtiene metadata del usuario actual."""
        try:
            user = supabase.auth.get_user()
            if user and user.user:
                return user.user.user_metadata
            return None
        except Exception as e:
            print(f"❌ Error obteniendo metadata: {e}")
            return None
