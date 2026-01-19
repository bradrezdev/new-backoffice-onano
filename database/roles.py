import reflex as rx

from sqlmodel import Field, SQLModel
from enum import Enum

class Roles(SQLModel, table=True):
    """
    Roles asignados a usuarios.
    Permite un sistema de permisos flexible basado en roles.
    """
    # Clave primaria
    role_id: int | None = Field(default=None, primary_key=True)

    # Información del rol
    role_name: str = Field(default="user")