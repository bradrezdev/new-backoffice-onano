"""
Modelos de base de datos para rangos de usuarios.
"""

import reflex as rx
from sqlmodel import SQLModel, Field

class Ranks(SQLModel, table=True):
    """
    Modelo de rangos de usuarios en el sistema.
    Define los diferentes rangos que un usuario puede alcanzar basado en puntos y otros criterios.
    """
    id: int | None = Field(default=None, primary_key=True)

    # Nombre del rango (único)
    name: str = Field(unique=True, index=True)

    # Puntos necesarios para alcanzar este rango (PV personal mínimo)
    pv_required: int = Field(default=0)

    # Puntos grupales necesarios (PVG grupal mínimo)
    pvg_required: int = Field(default=0)

    # Umbral mínimo de PVG para este rango (usado en calculate_rank)
    min_pvg: int | None = Field(default=None, index=True)