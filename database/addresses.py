import reflex as rx
from sqlmodel import SQLModel, Field, ForeignKey
from enum import Enum


# ✅ Mantener Countries SOLO para product_service (fuera del scope del registro)
class Countries(Enum):
    USA = "USA"
    COLOMBIA = "COLOMBIA"
    MEXICO = "MEXICO"
    PUERTO_RICO = "PUERTO_RICO"


class Addresses(SQLModel, table=True):
    """
    Tabla de direcciones.
    Contiene información de direcciones asociadas a usuarios.
    """
    id: int | None = Field(default=None, primary_key=True)

    # Información de dirección
    street: str = Field()
    neighborhood: str = Field()
    city: str = Field()
    state: str = Field()
    country: str = Field(max_length=50)  # ✅ Texto plano en lugar de ENUM
    zip_code: str = Field()