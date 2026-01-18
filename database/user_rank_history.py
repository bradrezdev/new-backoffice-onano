import reflex as rx
from sqlmodel import SQLModel, Field, func
from datetime import datetime, date, timezone
from NNProtect_new_website.utils.timezone_mx import get_mexico_now

class UserRankHistory(SQLModel, table=True):
    """
    Historial de rangos con timestamps en UTC puro.
    """
    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(index=True, foreign_key="users.member_id")
    rank_id: int = Field(default=None, index=True, foreign_key="ranks.id")

    # Timestamp en UTC puro (conversión a timezone local en UI)
    achieved_on: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )

    period_id: int | None = Field(default=None, index=True, foreign_key="periods.id")