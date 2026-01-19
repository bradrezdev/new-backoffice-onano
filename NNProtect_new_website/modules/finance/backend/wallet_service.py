"""
Servicio POO para gestión de billetera virtual.
Maneja depósitos, retiros, transferencias y pagos con wallet.

Principios aplicados: KISS, DRY, YAGNI, POO
CRÍTICO: Todas las operaciones son atómicas (todo o nada)
"""

import sqlmodel
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from database.wallet import (
    Wallets, WalletTransactions, WalletWithdrawals,
    WalletStatus, WalletTransactionType, WalletTransactionStatus, WithdrawalStatus
)
from database.comissions import Commissions, CommissionStatus


class WalletService:
    """
    Servicio POO para gestión de billetera virtual.
    Principio POO: Encapsula toda la lógica de negocio de wallet.
    """

    @classmethod
    def create_wallet(cls, session, member_id: int, currency: str) -> Optional[int]:
        """
        Crea una billetera para un usuario.
        Principio KISS: Una wallet por usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            currency: Moneda (MXN, USD, COP, DOP)

        Returns:
            ID de wallet creada o None si falla
        """
        try:
            # Verificar si ya existe una wallet
            existing_wallet = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
            ).first()

            if existing_wallet:
                print(f"⚠️  Usuario {member_id} ya tiene una wallet (ID: {existing_wallet.id})")
                return existing_wallet.id

            # Crear nueva wallet
            wallet = Wallets(
                member_id=member_id,
                balance=0.0,
                currency=currency,
                status=WalletStatus.ACTIVE.value
            )

            session.add(wallet)
            session.flush()

            print(f"✅ Wallet creada para usuario {member_id} (ID: {wallet.id})")
            return wallet.id

        except Exception as e:
            print(f"❌ Error creando wallet para usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def get_wallet_balance(cls, session, member_id: int) -> Optional[float]:
        """
        Obtiene el balance actual de la wallet de un usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario

        Returns:
            Balance actual o None si no existe wallet
        """
        try:
            wallet = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
            ).first()

            return wallet.balance if wallet else None

        except Exception as e:
            print(f"❌ Error obteniendo balance de usuario {member_id}: {e}")
            return None

    @classmethod
    def deposit_commission(
        cls,
        session,
        member_id: int,
        commission_id: int,
        amount: float,
        currency: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Deposita una comisión en la wallet del usuario.
        Principio: Atomicidad - todo o nada.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario receptor
            commission_id: ID de la comisión
            amount: Monto a depositar
            currency: Moneda
            description: Descripción opcional

        Returns:
            True si se completó exitosamente, False si falló
        """
        try:
            # 1. Obtener wallet
            wallet = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
            ).first()

            if not wallet:
                print(f"❌ No existe wallet para usuario {member_id}")
                return False

            if wallet.status != WalletStatus.ACTIVE.value:
                print(f"❌ Wallet de usuario {member_id} no está activa (status: {wallet.status})")
                return False

            # 2. Verificar que la comisión existe y está PENDING
            commission = session.get(Commissions, commission_id)
            if not commission:
                print(f"❌ Comisión {commission_id} no existe")
                return False

            if commission.status != CommissionStatus.PENDING.value:
                print(f"⚠️  Comisión {commission_id} ya fue procesada (status: {commission.status})")
                return False

            # 3. Crear transacción de wallet
            transaction_uuid = str(uuid.uuid4())
            balance_before = wallet.balance
            balance_after = balance_before + amount

            transaction = WalletTransactions(
                transaction_uuid=transaction_uuid,
                member_id=member_id,
                transaction_type=WalletTransactionType.COMMISSION_DEPOSIT.value,
                status=WalletTransactionStatus.COMPLETED.value,
                amount=amount,
                balance_before=balance_before,
                balance_after=balance_after,
                currency=currency,
                commission_id=commission_id,
                description=description or f"Depósito de comisión #{commission_id}",
                completed_at=datetime.now(timezone.utc)
            )

            session.add(transaction)

            # 4. Actualizar balance de wallet
            wallet.balance = balance_after
            wallet.updated_at = datetime.now(timezone.utc)

            # 5. Actualizar estado de comisión
            commission.status = CommissionStatus.PAID.value
            commission.paid_at = datetime.now(timezone.utc)

            session.flush()

            print(f"✅ Comisión #{commission_id} depositada en wallet de usuario {member_id}: +{amount} {currency}")
            return True

        except Exception as e:
            print(f"❌ Error depositando comisión {commission_id} a usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def pay_order_with_wallet(
        cls,
        session,
        member_id: int,
        order_id: int,
        amount: float,
        currency: str
    ) -> bool:
        """
        Paga una orden usando el balance de la wallet.
        Principio: Validación previa + atomicidad.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            order_id: ID de la orden
            amount: Monto a pagar
            currency: Moneda

        Returns:
            True si se completó exitosamente, False si falló
        """
        try:
            # 1. Obtener wallet
            wallet = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
            ).first()

            if not wallet:
                print(f"❌ No existe wallet para usuario {member_id}")
                return False

            # 2. Verificar que wallet esté ACTIVE
            if wallet.status != WalletStatus.ACTIVE.value:
                print(f"❌ Wallet de usuario {member_id} no está activa (status: {wallet.status})")
                return False

            # 3. Verificar balance suficiente
            if not wallet.has_sufficient_balance(amount):
                print(f"❌ Balance insuficiente: tiene {wallet.balance} {currency}, necesita {amount} {currency}")
                return False

            # 3. Crear transacción de débito
            transaction_uuid = str(uuid.uuid4())
            balance_before = wallet.balance
            balance_after = balance_before - amount

            transaction = WalletTransactions(
                transaction_uuid=transaction_uuid,
                member_id=member_id,
                transaction_type=WalletTransactionType.ORDER_PAYMENT.value,
                status=WalletTransactionStatus.COMPLETED.value,
                amount=-amount,  # Negativo para débito
                balance_before=balance_before,
                balance_after=balance_after,
                currency=currency,
                order_id=order_id,
                description=f"Pago de orden #{order_id}",
                completed_at=datetime.now(timezone.utc)
            )

            session.add(transaction)

            # 4. Actualizar balance de wallet
            wallet.balance = balance_after
            wallet.updated_at = datetime.now(timezone.utc)

            session.flush()

            print(f"✅ Orden #{order_id} pagada con wallet de usuario {member_id}: -{amount} {currency}")
            return True

        except Exception as e:
            print(f"❌ Error pagando orden {order_id} con wallet de usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def transfer_between_users(
        cls,
        session,
        from_member_id: int,
        to_member_id: int,
        amount: float,
        currency: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Transfiere saldo entre dos usuarios.
        Principio: Atomicidad - ambas transacciones o ninguna.

        Args:
            session: Sesión de base de datos
            from_member_id: Usuario que envía
            to_member_id: Usuario que recibe
            amount: Monto a transferir
            currency: Moneda
            description: Descripción opcional

        Returns:
            True si se completó exitosamente, False si falló
        """
        try:
            # 1. Obtener ambas wallets
            wallet_from = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == from_member_id)
            ).first()

            wallet_to = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == to_member_id)
            ).first()

            if not wallet_from or not wallet_to:
                print(f"❌ Una o ambas wallets no existen")
                return False

            # 2. Verificar balance suficiente
            if not wallet_from.has_sufficient_balance(amount):
                print(f"❌ Balance insuficiente en wallet origen")
                return False

            # 3. Crear transacción OUT (usuario que envía)
            transaction_out_uuid = str(uuid.uuid4())
            balance_from_before = wallet_from.balance
            balance_from_after = balance_from_before - amount

            transaction_out = WalletTransactions(
                transaction_uuid=transaction_out_uuid,
                member_id=from_member_id,
                transaction_type=WalletTransactionType.TRANSFER_OUT.value,
                status=WalletTransactionStatus.COMPLETED.value,
                amount=-amount,
                balance_before=balance_from_before,
                balance_after=balance_from_after,
                currency=currency,
                transfer_to_member_id=to_member_id,
                description=description or f"Transferencia a usuario {to_member_id}",
                completed_at=datetime.now(timezone.utc)
            )

            session.add(transaction_out)

            # 4. Crear transacción IN (usuario que recibe)
            transaction_in_uuid = str(uuid.uuid4())
            balance_to_before = wallet_to.balance
            balance_to_after = balance_to_before + amount

            transaction_in = WalletTransactions(
                transaction_uuid=transaction_in_uuid,
                member_id=to_member_id,
                transaction_type=WalletTransactionType.TRANSFER_IN.value,
                status=WalletTransactionStatus.COMPLETED.value,
                amount=amount,
                balance_before=balance_to_before,
                balance_after=balance_to_after,
                currency=currency,
                transfer_from_member_id=from_member_id,
                description=description or f"Transferencia de usuario {from_member_id}",
                completed_at=datetime.now(timezone.utc)
            )

            session.add(transaction_in)

            # 5. Actualizar ambos balances
            wallet_from.balance = balance_from_after
            wallet_from.updated_at = datetime.now(timezone.utc)

            wallet_to.balance = balance_to_after
            wallet_to.updated_at = datetime.now(timezone.utc)

            session.flush()

            print(f"✅ Transferencia exitosa: {from_member_id} -> {to_member_id}: {amount} {currency}")
            return True

        except Exception as e:
            print(f"❌ Error en transferencia {from_member_id} -> {to_member_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def request_withdrawal(
        cls,
        session,
        member_id: int,
        amount: float,
        currency: str,
        bank_name: str,
        account_number: str,
        account_holder_name: str
    ) -> Optional[int]:
        """
        Crea una solicitud de retiro a cuenta bancaria.
        Principio: El dinero se reserva pero no se retira hasta aprobar.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            amount: Monto a retirar
            currency: Moneda
            bank_name: Nombre del banco
            account_number: Número de cuenta
            account_holder_name: Titular de la cuenta

        Returns:
            ID de solicitud de retiro o None si falla
        """
        try:
            # 1. Obtener wallet
            wallet = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
            ).first()

            if not wallet:
                print(f"❌ No existe wallet para usuario {member_id}")
                return None

            # 2. Verificar balance suficiente
            if not wallet.has_sufficient_balance(amount):
                print(f"❌ Balance insuficiente para retiro")
                return None

            # 3. Crear transacción de wallet (PENDING)
            transaction_uuid = str(uuid.uuid4())
            balance_before = wallet.balance
            balance_after = balance_before - amount

            transaction = WalletTransactions(
                transaction_uuid=transaction_uuid,
                member_id=member_id,
                transaction_type=WalletTransactionType.WITHDRAWAL_REQUEST.value,
                status=WalletTransactionStatus.PENDING.value,
                amount=-amount,
                balance_before=balance_before,
                balance_after=balance_after,
                currency=currency,
                description=f"Solicitud de retiro"
            )

            session.add(transaction)
            session.flush()

            # 4. Crear registro de retiro
            withdrawal = WalletWithdrawals(
                member_id=member_id,
                wallet_transaction_id=transaction.id,
                amount=amount,
                currency=currency,
                bank_name=bank_name,
                account_number=account_number,  # ⚠️ ENCRIPTAR EN PRODUCCIÓN
                account_holder_name=account_holder_name,
                status=WithdrawalStatus.PENDING.value
            )

            session.add(withdrawal)

            # 5. Actualizar balance de wallet
            wallet.balance = balance_after
            wallet.updated_at = datetime.now(timezone.utc)

            session.flush()

            print(f"✅ Solicitud de retiro creada para usuario {member_id}: {amount} {currency} (ID: {withdrawal.id})")
            return withdrawal.id

        except Exception as e:
            print(f"❌ Error creando solicitud de retiro para usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def get_transaction_history(
        cls,
        session,
        member_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """
        Obtiene el historial de transacciones de un usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Lista de transacciones
        """
        try:
            transactions = session.exec(
                sqlmodel.select(WalletTransactions)
                .where(WalletTransactions.member_id == member_id)
                .order_by(sqlmodel.desc(WalletTransactions.created_at))
                .limit(limit)
                .offset(offset)
            ).all()

            return list(transactions)

        except Exception as e:
            print(f"❌ Error obteniendo historial de transacciones de usuario {member_id}: {e}")
            return []

    @classmethod
    def process_pending_commissions_to_wallet(cls, session, period_id: int) -> int:
        """
        Procesa todas las comisiones PENDING de un período y las deposita en wallets.
        Principio: Procesamiento batch con atomicidad individual.

        Args:
            session: Sesión de base de datos
            period_id: ID del período

        Returns:
            Cantidad de comisiones procesadas exitosamente
        """
        try:
            # Obtener todas las comisiones PENDING del período
            pending_commissions = session.exec(
                sqlmodel.select(Commissions)
                .where(
                    (Commissions.period_id == period_id) &
                    (Commissions.status == CommissionStatus.PENDING.value)
                )
            ).all()

            processed_count = 0

            for commission in pending_commissions:
                # Depositar cada comisión en su wallet
                success = cls.deposit_commission(
                    session=session,
                    member_id=commission.member_id,
                    commission_id=commission.id,
                    amount=commission.amount_converted,
                    currency=commission.currency_destination,
                    description=f"Comisión {commission.bonus_type} - Período {period_id}"
                )

                if success:
                    processed_count += 1

            session.commit()

            print(f"✅ Procesadas {processed_count}/{len(pending_commissions)} comisiones del período {period_id}")
            return processed_count

        except Exception as e:
            print(f"❌ Error procesando comisiones del período {period_id}: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return 0
