import reflex as rx
from sqlmodel import SQLModel, Field, ForeignKey

class UnilevelReports(SQLModel, table=True):
    """
    Tabla de reportes unilevel.
    Contiene información de reportes unilevel asociados a usuarios.
    """
    id: int | None = Field(default=None, primary_key=True)

    # Vinculo con usuario
    user_id: int = Field(foreign_key="users.id", index=True)

    # Información del reporte
    period_id: int = Field(foreign_key="periods.id", index=True)
    pv: int = Field(default=0)
    vn: float = Field(default=0.0)
    pvg_1: int = Field(default=0)
    vng_1: float = Field(default=0.0)
    pvg_2: int = Field(default=0)
    vng_2: float = Field(default=0.0)
    pvg_3: int = Field(default=0)
    vng_3: float = Field(default=0.0)
    pvg_4: int = Field(default=0)
    vng_4: float = Field(default=0.0)
    pvg_5: int = Field(default=0)
    vng_5: float = Field(default=0.0)
    pvg_6: int = Field(default=0)
    vng_6: float = Field(default=0.0)
    pvg_7: int = Field(default=0)
    vng_7: float = Field(default=0.0)
    pvg_8: int = Field(default=0)
    vng_8: float = Field(default=0.0)
    pvg_9: int = Field(default=0)
    vng_9: float = Field(default=0.0)
    pvg_10_plus: int = Field(default=0)
    vng_10_plus: float = Field(default=0.0)
    pvg_total: int = Field(default=0)
    vng_total: float = Field(default=0.0)