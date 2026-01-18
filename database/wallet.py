import reflex as rx
from sqlmodel import SQLModel, Field, func, Index, CheckConstraint
from datetime import datetime, timezone
from enum import Enum
import uuid


class WalletStatus(Enum):
    """Estados de billetera"""
    ACTIVE = "ACTIVE"           # Activa
    SUSPENDED = "SUSPENDED"     # Suspendida temporalmente
    CLOSED = "CLOSED"           # Cerrada permanentemente


class WalletTransactionType(Enum):
    """Tipos de transacciones de billetera"""
    # Entradas (créditos)
    COMMISSION_DEPOSIT = "commission_deposit"       # Depósito de comisión
    TRANSFER_IN = "transfer_in"                    # Transferencia recibida
    REFUND = "refund"                              # Devolución
    ADJUSTMENT_CREDIT = "adjustment_credit"        # Ajuste administrativo positivo

    # Salidas (débitos)
    ORDER_PAYMENT = "order_payment"                # Pago de orden
    TRANSFER_OUT = "transfer_out"                  # Transferencia enviada
    WITHDRAWAL_REQUEST = "withdrawal_request"      # Solicitud de retiro
    WITHDRAWAL_COMPLETED = "withdrawal_completed"  # Retiro completado
    WITHDRAWAL_REJECTED = "withdrawal_rejected"    # Retiro rechazado (reversa)
    ADJUSTMENT_DEBIT = "adjustment_debit"          # Ajuste administrativo negativo


class WalletTransactionStatus(Enum):
    """Estados de transacción"""
    PENDING = "pending"         # Pendiente
    COMPLETED = "completed"     # Completada
    FAILED = "failed"          # Fallida
    CANCELLED = "cancelled"    # Cancelada


class WithdrawalStatus(Enum):
    """Estados de solicitud de retiro"""
    PENDING = "PENDING"         # Pendiente de procesamiento
    PROCESSING = "PROCESSING"   # En procesamiento
    COMPLETED = "COMPLETED"     # Completado
    REJECTED = "REJECTED"       # Rechazado


class Wallets(SQLModel, table=True):
    """
    Billetera virtual por usuario (una por usuario).
    Almacena el balance actual y el estado de la wallet.

    CRÍTICO: El balance NUNCA puede ser negativo (CHECK CONSTRAINT).
    """
    __tablename__ = "wallets"

    __table_args__ = (
        CheckConstraint('balance >= 0', name='balance_non_negative'),
        Index('idx_wallet_member', 'member_id'),
        Index('idx_wallet_status', 'status'),
    )

    id: int | None = Field(default=None, primary_key=True)


    # Usuario (único)
    member_id: int = Field(foreign_key="users.member_id", unique=True, index=True)

    # Balance actual (NUNCA negativo)
    balance: float = Field(default=0.0)

    # Moneda (según país del usuario)
    currency: str = Field(max_length=10)  # MXN, USD, COP, DOP

    # Estado de la billetera
    status: str = Field(default=WalletStatus.ACTIVE.value, max_length=20, index=True)

    # Timestamps (UTC puro)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()}
    )

    def has_sufficient_balance(self, amount: float) -> bool:
        """Verifica si hay balance suficiente para una transacción."""
        return self.balance >= amount

    def __repr__(self):
        return f"<Wallet(member_id={self.member_id}, balance={self.balance} {self.currency}, status={self.status})>"


class WalletTransactions(SQLModel, table=True):
    """
    Registro inmutable de todas las transacciones de billetera.
    CADA transacción debe quedar registrada permanentemente.

    Características críticas:
    - Inmutabilidad: Una vez creado, NUNCA se modifica
    - Idempotencia: transaction_uuid evita duplicados
    - Auditoría completa: balance_before + balance_after
    """
    __tablename__ = "wallettransactions"
    
    id: int | None = Field(default=None, primary_key=True)

    __table_args__ = (
        Index('idx_wt_member_type', 'member_id', 'transaction_type'),
        Index('idx_wt_member_status', 'member_id', 'status'),
        Index('idx_wt_member_created', 'member_id', 'created_at'),
        Index('idx_wt_commission', 'commission_id'),
        Index('idx_wt_order', 'order_id'),
        Index('idx_wt_uuid', 'transaction_uuid'),
    )

    # UUID para idempotencia (evita duplicados)
    transaction_uuid: str = Field(unique=True, index=True, default_factory=lambda: str(uuid.uuid4()))

    # Usuario propietario de la wallet
    member_id: int = Field(foreign_key="users.member_id", index=True)

    # Tipo y estado de la transacción
    transaction_type: str = Field(max_length=50, index=True)  # Enum WalletTransactionType
    status: str = Field(default=WalletTransactionStatus.PENDING.value, max_length=20, index=True)

    # Montos (puede ser negativo para débitos)
    amount: float  # Monto de la transacción (+ para crédito, - para débito)
    balance_before: float  # Balance ANTES de la transacción
    balance_after: float  # Balance DESPUÉS de la transacción
    currency: str = Field(max_length=10)

    # Referencias externas (opcionales según tipo de transacción)
    commission_id: int | None = Field(default=None, foreign_key="commissions.id", index=True)
    order_id: int | None = Field(default=None, foreign_key="orders.id", index=True)
    transfer_to_member_id: int | None = Field(default=None, foreign_key="users.member_id")
    transfer_from_member_id: int | None = Field(default=None, foreign_key="users.member_id")

    # Metadatos
    description: str = Field(max_length=500)  # Descripción legible
    notes: str | None = Field(default=None, max_length=500)
    metadata_json: str | None = Field(default=None)  # JSON para datos adicionales

    # Timestamps (UTC puro)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    completed_at: datetime | None = Field(default=None)

    def mark_as_completed(self):
        """Marca la transacción como completada."""
        self.status = WalletTransactionStatus.COMPLETED.value
        self.completed_at = datetime.now(timezone.utc)

    def mark_as_failed(self, reason: str):
        """Marca la transacción como fallida."""
        self.status = WalletTransactionStatus.FAILED.value
        self.notes = reason

    def __repr__(self):
        return f"<WalletTransaction(id={self.id}, member_id={self.member_id}, type={self.transaction_type}, amount={self.amount}, status={self.status})>"


class WalletWithdrawals(SQLModel, table=True):
    """
    Solicitudes de retiro a cuenta bancaria.
    Registra todas las solicitudes de retiro con datos bancarios.

    IMPORTANTE: Los datos bancarios deben estar encriptados en producción.
    """
    __tablename__ = "walletwithdrawals"

    __table_args__ = (
        Index('idx_ww_member', 'member_id'),
        Index('idx_ww_status', 'status'),
        Index('idx_ww_requested', 'requested_at'),
    )

    id: int | None = Field(default=None, primary_key=True)


    # Usuario
    member_id: int = Field(foreign_key="users.member_id", index=True)

    
    # Transacción de wallet asociada
    wallet_transaction_id: int = Field(foreign_key="wallettransactions.id", unique=True, index=True)

    # Monto solicitado
    amount: float
    currency: str = Field(max_length=10)

    # Datos bancarios (⚠️ ENCRIPTAR EN PRODUCCIÓN)
    bank_name: str = Field(max_length=100)
    account_number: str = Field(max_length=50)
    account_holder_name: str = Field(max_length=150)

    # Estado y procesamiento
    status: str = Field(default=WithdrawalStatus.PENDING.value, max_length=20, index=True)
    rejection_reason: str | None = Field(default=None, max_length=500)

    # Timestamps (UTC puro)
    requested_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()}
    )
    processed_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    def mark_as_processing(self):
        """Marca el retiro como en procesamiento."""
        self.status = WithdrawalStatus.PROCESSING.value
        self.processed_at = datetime.now(timezone.utc)

    def mark_as_completed(self):
        """Marca el retiro como completado."""
        self.status = WithdrawalStatus.COMPLETED.value
        self.completed_at = datetime.now(timezone.utc)

    def mark_as_rejected(self, reason: str):
        """Marca el retiro como rechazado."""
        self.status = WithdrawalStatus.REJECTED.value
        self.rejection_reason = reason
        self.processed_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f"<WalletWithdrawal(member_id={self.member_id}, amount={self.amount} {self.currency}, status={self.status})>"
