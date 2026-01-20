from typing import Dict, Any

class UserDataService:
    """Helper para formateo de datos de usuario en la UI de autenticación."""
    
    @staticmethod
    def extract_first_word(text: str) -> str:
        tokens = str(text or "").strip().split()
        return tokens[0] if tokens else ""

    @classmethod
    def build_profile_name(cls, first_name: str, last_name: str, username: str) -> str:
        first = cls.extract_first_word(first_name)
        last = cls.extract_first_word(last_name)
        
        if first and last:
            return f"{first} {last}"
        elif first:
            return first
        elif last:
            return last
        else:
            return username or "Usuario"

    @staticmethod
    def load_user_profile_data(user_id: int) -> Dict[str, Any]:
        """Placeholder para cargar perfil completo."""
        return {"user_id": user_id, "loaded": True}

    @staticmethod
    def get_user_country_by_id(user_id: int) -> str:
        """
        Obtiene el país del usuario basado en su dirección principal.
        """
        import reflex as rx
        from sqlmodel import select
        from database.addresses import Addresses
        from database.users_addresses import UserAddresses
        
        try:
            with rx.session() as session:
                # Intentar obtener dirección marcada como default
                statement = (
                    select(Addresses.country)
                    .join(UserAddresses, Addresses.id == UserAddresses.address_id)
                    .where(UserAddresses.user_id == user_id)
                    .where(UserAddresses.is_default == True)
                )
                country = session.exec(statement).first()
                
                # Si no hay dirección por defecto, intentar cualquiera asociada al usuario
                if not country:
                    statement = (
                        select(Addresses.country)
                        .join(UserAddresses, Addresses.id == UserAddresses.address_id)
                        .where(UserAddresses.user_id == user_id)
                    )
                    country = session.exec(statement).first()
                
                return country if country else ""
        except Exception as e:
            print(f"Error fetching user country for user_id {user_id}: {e}")
            return ""
