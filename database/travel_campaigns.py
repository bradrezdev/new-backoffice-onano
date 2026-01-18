import reflex as rx
from sqlmodel import SQLModel, Field, func, Index, UniqueConstraint
from datetime import datetime, timezone
from enum import Enum


class CampaignStatus(Enum):
    """Estados de campaña de NN Travel"""
    ACTIVE = "active"
    CLOSED = "closed"


class TravelEventType(Enum):
    """Tipos de eventos que generan puntos NN Travel"""
    KIT_PURCHASE = "kit_purchase"           # Compra de kit en la red
    SELF_RANK = "self_rank"                 # Rango alcanzado por el usuario
    DIRECT_RANK = "direct_rank"             # Rango alcanzado por directo
    BONUS = "bonus"                         # Bonificación especial (5 Full Protect)


class TravelCampaigns(SQLModel, table=True):
    """
    Campañas semestrales de NN Travels.
    Cada campaña dura 6 meses y tiene una meta de puntos (default: 200).
    """
    __tablename__ = "travelcampaigns"

    id: int | None = Field(default=None, primary_key=True)

    # Identificación de la campaña
    name: str = Field(max_length=100, unique=True, index=True)  # "Campaña 2025-H1"
    description: str | None = Field(default=None, max_length=255)

    # Fechas de la campaña
    start_date: datetime = Field(index=True)
    end_date: datetime = Field(index=True)

    # Configuración de puntos
    target_points: int = Field(default=200)  # Meta de puntos para calificar
    is_promo_active: bool = Field(default=False)  # Si hay puntos duplicados

    # Relación con período
    period_id: int = Field(foreign_key="periods.id", index=True)

    # Estado de la campaña
    status: str = Field(default=CampaignStatus.ACTIVE.value, max_length=20, index=True)

    # Timestamps (UTC puro)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()}
    )

    def __repr__(self):
        return f"<TravelCampaign(id={self.id}, name='{self.name}', status={self.status})>"


class NNTravelPoints(SQLModel, table=True):
    """
    Acumulación de puntos NN Travel por usuario y campaña.
    Registro único por member_id + campaign_id.
    """
    __tablename__ = "nntravelpoints"

    __table_args__ = (
        UniqueConstraint('member_id', 'campaign_id', name='uq_member_campaign'),
        Index('idx_nntp_member_campaign', 'member_id', 'campaign_id'),
        Index('idx_nntp_campaign', 'campaign_id'),
        Index('idx_nntp_qualifies', 'qualifies_for_travel'),
    )

    id: int | None = Field(default=None, primary_key=True)

    # Usuario y campaña
    member_id: int = Field(foreign_key="users.member_id", index=True)
    campaign_id: int = Field(foreign_key="travelcampaigns.id", index=True)

    # Desglose de puntos por fuente
    points_from_kits: int = Field(default=0)           # Puntos por kits vendidos en la red
    points_from_self_ranks: int = Field(default=0)     # Puntos por rangos propios
    points_from_direct_ranks: int = Field(default=0)   # Puntos por rangos de directos
    points_bonus: int = Field(default=0)               # Bonificaciones especiales

    # Total acumulado
    total_points: int = Field(default=0, index=True)

    # Calificación para el viaje
    qualifies_for_travel: bool = Field(default=False, index=True)

    # Timestamps (UTC puro)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()}
    )

    def update_qualification(self, target_points: int = 200):
        """Actualiza si el usuario califica basado en el total de puntos."""
        self.qualifies_for_travel = self.total_points >= target_points

    def recalculate_total(self):
        """Recalcula el total de puntos sumando todas las fuentes."""
        self.total_points = (
            self.points_from_kits +
            self.points_from_self_ranks +
            self.points_from_direct_ranks +
            self.points_bonus
        )

    def __repr__(self):
        return f"<NNTravelPoints(member_id={self.member_id}, campaign_id={self.campaign_id}, total={self.total_points}, qualifies={self.qualifies_for_travel})>"


class NNTravelPointsHistory(SQLModel, table=True):
    """
    Historial detallado de cada evento que genera puntos NN Travel.
    Registro inmutable para auditoría completa.
    """
    __tablename__ = "nntravelpointshistory"

    __table_args__ = (
        Index('idx_nntph_member', 'member_id'),
        Index('idx_nntph_campaign', 'campaign_id'),
        Index('idx_nntph_member_created', 'member_id', 'created_at'),
        Index('idx_nntph_event_type', 'event_type'),
    )

    id: int | None = Field(default=None, primary_key=True)

    # Usuario y campaña
    member_id: int = Field(foreign_key="users.member_id", index=True)
    campaign_id: int = Field(foreign_key="travelcampaigns.id", index=True)

    # Tipo de evento y puntos ganados
    event_type: str = Field(max_length=50, index=True)  # Enum TravelEventType
    points_earned: int  # Puntos ganados en este evento

    # Referencias opcionales según el tipo de evento
    source_member_id: int | None = Field(default=None, foreign_key="users.member_id")  # Si viene de un directo
    source_order_id: int | None = Field(default=None, foreign_key="orders.id")         # Si viene de compra de kit
    rank_achieved: str | None = Field(default=None, max_length=100)                    # Si es por rango alcanzado

    # Descripción del evento
    description: str = Field(max_length=500)  # Descripción legible del evento

    # Timestamp (UTC puro) - Inmutable
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )

    def __repr__(self):
        return f"<NNTravelPointsHistory(member_id={self.member_id}, event={self.event_type}, points={self.points_earned})>"
