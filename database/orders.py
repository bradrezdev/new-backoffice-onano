import reflex as rx
from sqlmodel import SQLModel, Field, func
from datetime import datetime, timezone
from enum import Enum


class OrderStatus(Enum):
    """Estados posibles de una orden"""
    DRAFT = "draft"                          # Orden en carrito (no enviada)
    PENDING_PAYMENT = "pending_payment"      # Enviada, esperando pago
    PAYMENT_CONFIRMED = "payment_confirmed"  # Pago confirmado - TRIGGER COMISIONES
    PROCESSING = "processing"                # En preparación
    SHIPPED = "shipped"                      # Enviada al cliente
    DELIVERED = "delivered"                  # Entregada
    CANCELLED = "cancelled"                  # Cancelada
    REFUNDED = "refunded"                    # Reembolsada


class Orders(SQLModel, table=True):
    """
    Órdenes de compra mensuales.
    Una orden puede contener múltiples productos (OrderItems).
    Reemplaza completamente la tabla Transactions.
    """
    id: int | None = Field(default=None, primary_key=True)

    # Comprador
    member_id: int = Field(foreign_key="users.member_id", index=True)

    # País y moneda de la orden
    country: str = Field(max_length=50, index=True)
    currency: str = Field(max_length=10)  # MXN, USD, COP

    # Totales de la orden
    subtotal: float = Field(default=0.0)
    shipping_cost: float = Field(default=0.0)
    tax: float = Field(default=0.0)
    discount: float = Field(default=0.0)  # Cashback u otros descuentos
    total: float = Field(default=0.0)

    # Puntos totales generados por esta orden
    total_pv: int = Field(default=0)
    total_vn: float = Field(default=0.0)

    # Estado de la orden
    status: str = Field(default=OrderStatus.DRAFT.value, index=True)

    # Dirección de envío
    shipping_address_id: int | None = Field(default=None, foreign_key="addresses.id")

    # Timestamps críticos (UTC puro)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    submitted_at: datetime | None = Field(default=None)  # Cuando envía la orden
    payment_confirmed_at: datetime | None = Field(default=None, index=True)  # CRÍTICO: trigger comisiones
    shipped_at: datetime | None = Field(default=None)
    delivered_at: datetime | None = Field(default=None)

    # Período al que pertenece (asignado al confirmar pago)
    period_id: int | None = Field(default=None, foreign_key="periods.id", index=True)

    # Información de pago
    payment_method: str | None = Field(default=None, max_length=50)
    payment_reference: str | None = Field(default=None, unique=True, index=True)

    # Notas
    customer_notes: str | None = Field(default=None, max_length=500)
    admin_notes: str | None = Field(default=None, max_length=500)

    def __repr__(self):
        return f"<Order(id={self.id}, member_id={self.member_id}, status={self.status}, total={self.total})>"
