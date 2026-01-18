import reflex as rx
from enum import Enum
from sqlmodel import SQLModel, Field, func
from datetime import datetime, timezone

class BonusType(Enum):
    """Tipos de bonos del plan de compensación"""
    BONO_DIRECTO = "bono_directo"         # Bono Directo (25% del VN)
    BONO_RAPIDO = "bono_rapido"           # Bono por inscripción (instantáneo)
    BONO_UNINIVEL = "bono_uninivel"       # Comisión por niveles (mensual)
    BONO_MATCHING = "bono_matching"       # Matching bonus (mensual)
    BONO_ALCANCE = "bono_alcance"         # Por alcanzar rango (una vez)
    BONO_AUTOMOVIL = "bono_automovil"     # Rango Embajador Transformador+
    BONO_TRAVELS = "bono_travels"         # NN Travels
    BONO_CASHBACK = "bono_cashback"       # Descuento en compra
    BONO_LEALTAD = "bono_lealtad"         # Compras 1-7 del mes

class CommissionStatus(Enum):
    """Estados de una comisión"""
    PENDING = "pending"       # Calculada pero no pagada
    PAID = "paid"            # Ya pagada
    CANCELLED = "cancelled"  # Cancelada por alguna razón

class Commissions(SQLModel, table=True):
    """
    Registro de todas las comisiones generadas en el sistema.
    Almacena el monto en VN original y el monto convertido a la moneda del receptor.
    """
    
    # Receptor de la comisión
    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="users.member_id", index=True)
    
    # Tipo de bono
    bonus_type: str = Field(max_length=50, index=True)
    
    # Origen de la comisión (si aplica)
    source_member_id: int | None = Field(default=None, foreign_key="users.member_id", index=True)
    source_order_id: int | None = Field(default=None, foreign_key="orders.id", index=True)
    
    # Período y profundidad
    period_id: int = Field(foreign_key="periods.id", index=True)
    level_depth: int | None = Field(default=None)  # Para bono uninivel: 1, 2, 3...
    
    # Montos y conversión
    amount_vn: float = Field(default=0.0)  # Monto en VN del país origen
    currency_origin: str = Field(max_length=10)  # MXN, USD, COP
    
    amount_converted: float = Field(default=0.0)  # Monto convertido a moneda del receptor
    currency_destination: str = Field(max_length=10)  # Moneda del receptor
    exchange_rate: float = Field(default=1.0)  # Tasa usada para conversión
    
    # Estado y timestamps (UTC puro)
    status: str = Field(default=CommissionStatus.PENDING.value, index=True)
    calculated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    paid_at: datetime | None = Field(default=None)
    
    # Notas adicionales (opcional)
    notes: str | None = Field(default=None, max_length=500)