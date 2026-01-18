import reflex as rx
from sqlmodel import SQLModel, Field, func
from datetime import datetime, timezone


class ExchangeRates(SQLModel, table=True):
    """
    Tasas de cambio fijas establecidas por la compañía.
    Permite cambiar tasas en el futuro sin afectar comisiones pasadas.
    """

    # Par de monedas
    id: int | None = Field(default=None, primary_key=True)
    from_currency: str = Field(max_length=10, index=True)  # COP
    to_currency: str = Field(max_length=10, index=True)    # MXN

    # Tasa de cambio
    rate: float = Field(default=1.0)

    # Vigencia
    effective_from: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    effective_until: datetime | None = Field(default=None)

    # Metadatos
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    notes: str | None = Field(default=None, max_length=255)