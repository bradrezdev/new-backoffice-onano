import reflex as rx
from sqlmodel import Field, SQLModel
from datetime import datetime, date, timezone
from enum import Enum

class UserGender(Enum):
    """Género del usuario"""
    MALE = "MALE"                  # Masculino
    FEMALE = "FEMALE"                  # Femenino

class UserProfiles(SQLModel, table=True):
    """
    Perfiles extendidos de usuarios.
    Contiene información personal y de contacto adicional.
    """
    # Clave primaria compuesta con user_id
    user_id: int = Field(primary_key=True, foreign_key="users.id")

    # Información personal
    bio: str = Field(max_length=150, default="")  # Valor por defecto para compatibilidad
    gender: UserGender = Field(index=True)
    phone_number: str = Field(index=True)
    date_of_birth: date | None = Field(default=None)  # Corrección tipo
    photo_url: str | None = Field(default=None)  # Corrección tipo
    timezone: str = Field(default="UTC")