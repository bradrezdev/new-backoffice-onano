import reflex as rx
from sqlmodel import Field, SQLModel, func
from datetime import datetime, timezone

class UserAddresses(SQLModel, table=True):
    """Direcciones de usuario con timestamps en UTC puro."""
    user_id: int = Field(primary_key=True, foreign_key="users.id")
    address_id: int = Field(primary_key=True, foreign_key="addresses.id")
    address_name: str = Field(default=None, index=True)
    is_default: bool = Field(default=False)

    # Timestamps en UTC puro (conversión a timezone local en UI)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )