"""
Script rápido para probar el balance de wallet en mlm_data
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import reflex as rx
from NNProtect_new_website.modules.network.backend.mlm_user_manager import MLMUserManager
from NNProtect_new_website.modules.finance.backend.wallet_service import WalletService
from database.users import Users
import sqlmodel

def test_wallet_balance_in_mlm_data():
    """Prueba que el balance de wallet se incluye en mlm_data"""

    print("\n" + "="*80)
    print("  PRUEBA: Balance de Wallet en MLM Data")
    print("="*80 + "\n")

    with rx.session() as session:
        # Obtener primer usuario
        user = session.exec(
            sqlmodel.select(Users).where(Users.member_id == 1)
        ).first()

        if not user:
            print("❌ No se encontró usuario con member_id 1")
            return

        print(f"✅ Usuario encontrado: {user.first_name} {user.last_name}")
        print(f"   Supabase ID: {user.supabase_user_id}")

        # Asegurar que tiene wallet con saldo
        wallet_id = WalletService.create_wallet(session, user.member_id, "MXN")
        balance = WalletService.get_wallet_balance(session, user.member_id)

        print(f"\n💰 Balance actual: {balance} MXN")

        # Si balance es 0, añadir dinero de prueba
        if balance == 0:
            print("\n📝 Añadiendo 1000 MXN de prueba...")

            import uuid
            from database.wallet import Wallets, WalletTransactions, WalletTransactionType, WalletTransactionStatus
            from datetime import datetime, timezone

            wallet = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == user.member_id)
            ).first()

            transaction = WalletTransactions(
                transaction_uuid=str(uuid.uuid4()),
                member_id=user.member_id,
                transaction_type=WalletTransactionType.ADJUSTMENT_CREDIT.value,
                status=WalletTransactionStatus.COMPLETED.value,
                amount=1000.0,
                balance_before=0.0,
                balance_after=1000.0,
                currency="MXN",
                description="Saldo de prueba",
                completed_at=datetime.now(timezone.utc)
            )

            session.add(transaction)
            wallet.balance = 1000.0
            wallet.updated_at = datetime.now(timezone.utc)
            session.commit()

            print("✅ Saldo añadido: 1000 MXN")

        # Cargar datos completos del usuario
        print("\n🔄 Cargando datos completos del usuario...")

        if not user.supabase_user_id:
            print("❌ Usuario no tiene supabase_user_id")
            return

        mlm_data = MLMUserManager.load_complete_user_data(user.supabase_user_id)

        if not mlm_data:
            print("❌ No se pudieron cargar datos MLM")
            return

        # Verificar que wallet_balance está en mlm_data
        print("\n✅ Datos MLM cargados:")
        print(f"   Nombre: {mlm_data.get('full_name', 'N/A')}")
        print(f"   Member ID: {mlm_data.get('member_id', 'N/A')}")
        print(f"   PV: {mlm_data.get('pv_cache', 0)}")
        print(f"   PVG: {mlm_data.get('pvg_cache', 0)}")
        print(f"   Rango actual: {mlm_data.get('current_month_rank', 'N/A')}")

        # ✅ VERIFICACIÓN CRÍTICA
        if 'wallet_balance' in mlm_data and 'wallet_currency' in mlm_data:
            print(f"\n💰✅ WALLET BALANCE EN MLM_DATA:")
            print(f"   Balance: {mlm_data['wallet_balance']} {mlm_data['wallet_currency']}")
            print("\n🎉 ¡Prueba exitosa! El balance de wallet está disponible en mlm_data")
        else:
            print("\n❌ FALLO: wallet_balance NO está en mlm_data")
            print(f"   Claves disponibles: {list(mlm_data.keys())}")

if __name__ == "__main__":
    test_wallet_balance_in_mlm_data()
