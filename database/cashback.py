import reflex as rx
from sqlmodel import SQLModel, Field, func, Index
from datetime import datetime, timezone
from enum import Enum


class CashbackStatus(Enum):
    """Estados del cashback"""
    AVAILABLE = "AVAILABLE"     # Disponible para usar
    USED = "USED"              # Ya utilizado
    EXPIRED = "EXPIRED"        # Expirado (fin de mes)


class Cashback(SQLModel, table=True):
    """
    Registro de cashbacks generados y aplicados.

    Reglas críticas:
    - Requisito: 2,930 PV acumulados en una orden
    - Descuento: 70% del precio público de productos
    - Base de cálculo: precio público de TODOS los productos
    - Válido hasta: fin del mismo mes
    - Aplicable en: misma orden o siguiente compra del mes
    - Envío: NO tiene descuento (se cobra normal)
    """
    __tablename__ = "cashback"

    id: int | None = Field(default=None, primary_key=True)

    __table_args__ = (
        Index('idx_cb_member_period', 'member_id', 'period_id'),
        Index('idx_cb_status', 'status'),
        Index('idx_cb_expires', 'expires_at'),
        Index('idx_cb_generated_order', 'generated_by_order_id'),
        Index('idx_cb_applied_order', 'applied_to_order_id'),
    )

    # Usuario y período
    member_id: int = Field(foreign_key="users.member_id", index=True)
    period_id: int = Field(foreign_key="periods.id", index=True)

    # Orden que generó el cashback (alcanzó 2,930 PV)
    generated_by_order_id: int = Field(foreign_key="orders.id", index=True)
    pv_accumulated: int  # PV que generó el cashback (debe ser >= 2,930)

    # Monto del descuento (70% del precio público)
    discount_amount: float  # En moneda del usuario
    currency: str = Field(max_length=10)  # MXN, USD, COP, DOP

    # Orden donde se aplicó el descuento (puede ser la misma o una posterior)
    applied_to_order_id: int | None = Field(default=None, foreign_key="orders.id", index=True)

    # Vigencia
    issued_at: datetime  # Fecha de emisión
    expires_at: datetime  # Fin del mes

    # Estado
    status: str = Field(default=CashbackStatus.AVAILABLE.value, max_length=20, index=True)

    # Timestamps (UTC puro)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()}
    )

    def is_valid(self) -> bool:
        """Verifica si el cashback está disponible y no ha expirado."""
        now = datetime.now(timezone.utc)
        return (
            self.status == CashbackStatus.AVAILABLE.value and
            now <= self.expires_at
        )

    def mark_as_used(self, order_id: int):
        """Marca el cashback como utilizado."""
        self.applied_to_order_id = order_id
        self.status = CashbackStatus.USED.value

    def mark_as_expired(self):
        """Marca el cashback como expirado."""
        self.status = CashbackStatus.EXPIRED.value

    def __repr__(self):
        return f"<Cashback(member_id={self.member_id}, discount={self.discount_amount} {self.currency}, status={self.status})>"


class CashbackUsage(SQLModel, table=True):
    """
    Detalle de productos comprados con cashback.
    Registra qué productos específicos de una orden utilizaron el descuento del cashback.
    """
    __tablename__ = "cashbackusage"

    id: int | None = Field(default=None, primary_key=True)

    __table_args__ = (
        Index('idx_cbu_cashback', 'cashback_id'),
        Index('idx_cbu_order', 'order_id'),
        Index('idx_cbu_order_item', 'order_item_id'),
    )

    # Referencias
    cashback_id: int = Field(foreign_key="cashback.id", index=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    order_item_id: int = Field(foreign_key="orderitems.id", index=True)

    # Producto
    product_id: int = Field(foreign_key="products.id", index=True)
    quantity: int

    # Precios
    original_price: float  # Precio público
    discount_applied: float  # 70% del precio público
    final_price: float  # 30% del precio público

    # Timestamp (UTC puro) - Inmutable
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )

    def __repr__(self):
        return f"<CashbackUsage(cashback_id={self.cashback_id}, product_id={self.product_id}, qty={self.quantity}, final={self.final_price})>"
