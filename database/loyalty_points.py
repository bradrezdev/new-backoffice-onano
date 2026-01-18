import reflex as rx
from sqlmodel import SQLModel, Field, func, Index
from datetime import datetime, timezone
from enum import Enum


class LoyaltyStatus(Enum):
    """Estados del programa de lealtad"""
    ACUMULANDO = "ACUMULANDO"       # Usuario acumulando puntos
    CALIFICADO = "CALIFICADO"       # Alcanzó 100 puntos
    CANJEADO = "CANJEADO"           # Regalo entregado
    REINICIADO = "REINICIADO"       # Reseteo por falta de compra


class LoyaltyEventType(Enum):
    """Tipos de eventos de lealtad"""
    EARNED = "EARNED"               # Ganó puntos (compra en día 1-7)
    RESET = "RESET"                 # Reinicio a 0 por falta de compra
    REDEEMED = "REDEEMED"           # Canjeó los 100 puntos


class RewardType(Enum):
    """Tipos de recompensas de lealtad"""
    PAQUETE_5_SUPLEMENTOS = "paquete_5_suplementos"
    PAQUETE_3_SERUMS_2_CREMAS = "paquete_3_serums_2_cremas"


class RewardStatus(Enum):
    """Estados de entrega de recompensa"""
    PENDING = "PENDING"             # Pendiente de entrega
    DELIVERED = "DELIVERED"         # Ya entregada


class LoyaltyPoints(SQLModel, table=True):
    """
    Balance de puntos de lealtad por usuario.
    Registro único por usuario (member_id único).

    Reglas críticas:
    - 25 puntos por mes al comprar entre día 1-7
    - Meta: 100 puntos (4 meses consecutivos)
    - Si un mes NO compra en día 1-7 → RESETEO A 0
    """
    __tablename__ = "loyaltypoints"

    __table_args__ = (
        Index('idx_lp_member', 'member_id'),
        Index('idx_lp_status', 'status'),
        Index('idx_lp_consecutive', 'consecutive_months'),
    )

    id: int | None = Field(default=None, primary_key=True)


    # Usuario (único)
    member_id: int = Field(foreign_key="users.member_id", unique=True, index=True)

    # Balance de puntos (0-100, se reinicia al canjear o resetear)
    current_points: int = Field(default=0, index=True)

    # Meses consecutivos acumulados (0-4)
    consecutive_months: int = Field(default=0)

    # Fecha de última compra válida (entre día 1-7)
    last_valid_purchase_date: datetime | None = Field(default=None)

    # Estado del programa de lealtad
    status: str = Field(default=LoyaltyStatus.ACUMULANDO.value, max_length=20, index=True)

    # Timestamps (UTC puro)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()}
    )

    def add_points(self, purchase_date: datetime):
        """
        Añade 25 puntos por compra válida.
        Actualiza estado a CALIFICADO si alcanza 100 puntos.
        """
        self.current_points += 25
        self.consecutive_months += 1
        self.last_valid_purchase_date = purchase_date

        if self.current_points >= 100:
            self.status = LoyaltyStatus.CALIFICADO.value

    def reset_points(self):
        """Reinicia los puntos a 0 por falta de compra en ventana 1-7."""
        self.current_points = 0
        self.consecutive_months = 0
        self.status = LoyaltyStatus.REINICIADO.value

    def redeem_reward(self):
        """Canjea la recompensa después de entregar el regalo."""
        self.current_points = 0
        self.consecutive_months = 0
        self.status = LoyaltyStatus.CANJEADO.value

    def __repr__(self):
        return f"<LoyaltyPoints(member_id={self.member_id}, points={self.current_points}, months={self.consecutive_months}, status={self.status})>"


class LoyaltyPointsHistory(SQLModel, table=True):
    """
    Historial completo de acumulaciones/reinicios del programa de lealtad.
    Registro inmutable para auditoría.
    """
    __tablename__ = "loyaltypointshistory"

    __table_args__ = (
        Index('idx_lph_member', 'member_id'),
        Index('idx_lph_period', 'period_id'),
        Index('idx_lph_member_created', 'member_id', 'created_at'),
        Index('idx_lph_event_type', 'event_type'),
    )

    id: int | None = Field(default=None, primary_key=True)


    # Usuario y período
    member_id: int = Field(foreign_key="users.member_id", index=True)
    period_id: int = Field(foreign_key="periods.id", index=True)

    # Tipo de evento
    event_type: str = Field(max_length=20, index=True)  # Enum LoyaltyEventType

    # Cambio de puntos
    points_before: int  # Puntos antes del evento
    points_after: int   # Puntos después del evento
    points_change: int  # Cambio: +25, -100, etc.

    # Referencia a orden (si aplica)
    order_id: int | None = Field(default=None, foreign_key="orders.id")
    purchase_day: int | None = Field(default=None)  # Día del mes (1-31)

    # Descripción del evento
    description: str = Field(max_length=500)

    # Timestamp (UTC puro) - Inmutable
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )

    def __repr__(self):
        return f"<LoyaltyPointsHistory(member_id={self.member_id}, event={self.event_type}, change={self.points_change})>"


class LoyaltyRewards(SQLModel, table=True):
    """
    Registro de recompensas de lealtad entregadas.
    Rastrea qué usuarios han recibido sus regalos físicos.
    """
    __tablename__ = "loyaltyrewards"

    __table_args__ = (
        Index('idx_lr_member', 'member_id'),
        Index('idx_lr_status', 'status'),
        Index('idx_lr_earned', 'earned_at'),
    )

    id: int | None = Field(default=None, primary_key=True)


    # Usuario receptor
    member_id: int = Field(foreign_key="users.member_id", index=True)

    # Tipo de recompensa
    reward_type: str = Field(max_length=50)  # Enum RewardType

    # Orden de entrega (si aplica)
    delivery_order_id: int | None = Field(default=None, foreign_key="orders.id")

    # Fechas
    earned_at: datetime  # Cuándo completó 100 puntos
    delivered_at: datetime | None = Field(default=None)  # Cuándo se entregó físicamente

    # Estado de entrega
    status: str = Field(default=RewardStatus.PENDING.value, max_length=20, index=True)

    # Timestamps (UTC puro)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()}
    )

    def mark_as_delivered(self, delivery_order_id: int):
        """Marca la recompensa como entregada."""
        self.status = RewardStatus.DELIVERED.value
        self.delivery_order_id = delivery_order_id
        self.delivered_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f"<LoyaltyReward(member_id={self.member_id}, reward={self.reward_type}, status={self.status})>"
