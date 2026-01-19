import reflex as rx
import bcrypt
from sqlmodel import SQLModel, Field, func, UniqueConstraint
from typing import Optional
from enum import Enum
from datetime import datetime, date, timezone

# ✅ Usar timezone utility con resta de 6 horas
from NNProtect_new_website.utils.timezone_mx import get_mexico_now


class UserStatus(Enum):
    """Estados posibles de un usuario en el sistema"""
    NO_QUALIFIED = "NO_QUALIFIED"
    QUALIFIED = "QUALIFIED" 
    SUSPENDED = "SUSPENDED"

class Users(SQLModel, table=True):
    """
    Modelo principal de usuarios con timestamps en UTC puro.
    """
    __table_args__ = (
        UniqueConstraint('member_id', name='uq_users_member_id'),
    )
    
    id: int | None = Field(default=None, primary_key=True)

    # Vinculo con Supabase Auth - UUID del usuario en auth.users
    supabase_user_id: str | None = Field(default=None, index=True, unique=True)

    # Identificadores únicos
    member_id: int = Field(unique=True, index=True)

    # Nombres de la persona
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    
    # Cache de email para consultas rápidas (email real está en Supabase auth.users)
    email_cache: str | None = Field(default=None, index=True)
    
    # Cache del país de registro desde addresses
    country_cache: str | None = Field(default=None, max_length=50, index=True)  # ✅ Texto plano

    # Estado y estructura de red
    status: UserStatus = Field(default=UserStatus.NO_QUALIFIED)
    sponsor_id: int | None = Field(default=None, foreign_key="users.member_id")
    referral_link: str | None = Field(default=None, unique=True, index=True)

    # Cache de PV acumulado (Personal Volume)
    pv_cache: int = Field(default=0, index=True)

    # Cache de VN acumulado (Volumen de Negocio)
    vn_cache: float = Field(default=0.0, index=True)

    # Cache de PVG acumulado (Puntos de Volumen Grupal)
    pvg_cache: int = Field(default=0, index=True)

    # Timestamps en UTC puro (conversión a timezone local en UI)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    
    @property
    def full_name(self) -> str:
        """Nombre completo del usuario."""
        return f"{self.first_name} {self.last_name}".strip()