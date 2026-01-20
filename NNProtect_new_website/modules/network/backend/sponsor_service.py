import reflex as rx
import sqlmodel
from typing import Optional
from database.users import Users

class SponsorService:
    """
    Servicio de Dominio de Red (Network).
    Maneja la lógica de patrocinadores y estructura MLM.
    """
    
    @staticmethod
    def validate_sponsor_by_member_id(member_id: int) -> bool:
        """Verifica si un ID de miembro es válido en el sistema."""
        if member_id <= 0:
            return False
            
        try:
            with rx.session() as session:
                sponsor = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == member_id)
                ).first()
                return sponsor is not None
        except Exception:
            # En producción, usar un logger real
            return False

    @staticmethod
    def get_user_id_by_member_id(member_id: int) -> Optional[int]:
        """Traduce un member_id público a un ID interno de base de datos."""
        try:
            with rx.session() as session:
                user = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == member_id)
                ).first()
                return user.id if user else None
        except Exception:
            return None

    @staticmethod
    def get_sponsor_display_name(member_id: int) -> str:
        """Obtiene el nombre formateado de un patrocinador."""
        if member_id <= 0:
            return "⚠️ Sin sponsor válido"
        
        try:
            with rx.session() as session:
                sponsor = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == member_id)
                ).first()
                if sponsor:
                    name = f"{sponsor.first_name or ''} {sponsor.last_name or ''}".strip()
                    return name or f"Socio #{sponsor.member_id}"
        except Exception:
            pass
        
        return "Socio desconocido"
