"""
Script de prueba para validar el sistema de Wallet, Cashback, Loyalty y Travel Points.
Este script prueba todas las funcionalidades críticas de los nuevos sistemas.

Ejecutar: python testers/test_wallet_points_systems.py
"""

import sys
import os

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import reflex as rx
from datetime import datetime, timezone, timedelta
from calendar import monthrange

from database.users import Users
from database.wallet import Wallets, WalletTransactions, WalletTransactionType
from database.cashback import Cashback, CashbackStatus
from database.loyalty_points import LoyaltyPoints, LoyaltyStatus
from database.travel_campaigns import TravelCampaigns, NNTravelPoints, CampaignStatus
from database.comissions import Commissions, CommissionStatus
from database.periods import Periods

from NNProtect_new_website.mlm_service.wallet_service import WalletService
from NNProtect_new_website.mlm_service.cashback_service import CashbackService
from NNProtect_new_website.mlm_service.loyalty_service import LoyaltyService
from NNProtect_new_website.mlm_service.travel_points_service import TravelPointsService


def print_header(title: str):
    """Imprime un header bonito para las secciones de prueba"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_wallet_creation():
    """Prueba 1: Creación de wallet"""
    print_header("PRUEBA 1: Creación de Wallet")

    with rx.session() as session:
        # Obtener el primer usuario
        user = session.query(Users).filter(Users.member_id == 1).first()

        if not user:
            print("❌ No se encontró usuario con member_id 1")
            return False

        # Crear wallet
        wallet_id = WalletService.create_wallet(
            session=session,
            member_id=user.member_id,
            currency="MXN"
        )

        if wallet_id:
            # Verificar balance inicial
            balance = WalletService.get_wallet_balance(session, user.member_id)
            print(f"✅ Wallet creada exitosamente")
            print(f"   ID: {wallet_id}")
            print(f"   Balance inicial: {balance} MXN")
            session.commit()
            return True
        else:
            print("❌ Falló la creación de wallet")
            session.rollback()
            return False


def test_commission_deposit():
    """Prueba 2: Depósito de comisión a wallet"""
    print_header("PRUEBA 2: Depósito de Comisión a Wallet")

    with rx.session() as session:
        user = session.query(Users).filter(Users.member_id == 1).first()
        if not user:
            print("❌ Usuario no encontrado")
            return False

        # Crear una comisión de prueba si no existe
        period = session.query(Periods).first()
        if not period:
            print("❌ No hay períodos en la BD")
            return False

        # Crear comisión PENDING
        commission = Commissions(
            member_id=user.member_id,
            bonus_type="bono_rapido",
            period_id=period.id,
            amount_vn=500.0,
            currency_origin="MXN",
            amount_converted=500.0,
            currency_destination="MXN",
            status=CommissionStatus.PENDING.value
        )

        session.add(commission)
        session.flush()

        print(f"📝 Comisión creada (ID: {commission.id}): 500 MXN")

        # Depositar en wallet
        success = WalletService.deposit_commission(
            session=session,
            member_id=user.member_id,
            commission_id=commission.id,
            amount=500.0,
            currency="MXN"
        )

        if success:
            balance = WalletService.get_wallet_balance(session, user.member_id)
            print(f"✅ Comisión depositada exitosamente")
            print(f"   Nuevo balance: {balance} MXN")
            session.commit()
            return True
        else:
            print("❌ Falló el depósito de comisión")
            session.rollback()
            return False


def test_wallet_transfer():
    """Prueba 3: Transferencia entre usuarios"""
    print_header("PRUEBA 3: Transferencia Entre Usuarios")

    with rx.session() as session:
        user1 = session.query(Users).filter(Users.member_id == 1).first()
        user2 = session.query(Users).filter(Users.member_id != 1).first()

        if not user1 or not user2:
            print("❌ Se necesitan al menos 2 usuarios")
            return False

        # Asegurar que user2 tenga wallet
        WalletService.create_wallet(session, user2.member_id, "MXN")

        balance_before_1 = WalletService.get_wallet_balance(session, user1.member_id)
        balance_before_2 = WalletService.get_wallet_balance(session, user2.member_id)

        print(f"📊 Balances antes:")
        print(f"   Usuario {user1.member_id}: {balance_before_1} MXN")
        print(f"   Usuario {user2.member_id}: {balance_before_2} MXN")

        # Transferir 100 MXN
        success = WalletService.transfer_between_users(
            session=session,
            from_member_id=user1.member_id,
            to_member_id=user2.member_id,
            amount=100.0,
            currency="MXN",
            description="Transferencia de prueba"
        )

        if success:
            balance_after_1 = WalletService.get_wallet_balance(session, user1.member_id)
            balance_after_2 = WalletService.get_wallet_balance(session, user2.member_id)

            print(f"✅ Transferencia exitosa")
            print(f"📊 Balances después:")
            print(f"   Usuario {user1.member_id}: {balance_after_1} MXN")
            print(f"   Usuario {user2.member_id}: {balance_after_2} MXN")
            session.commit()
            return True
        else:
            print("❌ Falló la transferencia")
            session.rollback()
            return False


def test_cashback_generation():
    """Prueba 4: Generación de cashback"""
    print_header("PRUEBA 4: Generación de Cashback")

    with rx.session() as session:
        user = session.query(Users).filter(Users.member_id == 1).first()
        period = session.query(Periods).first()

        if not user or not period:
            print("❌ Usuario o período no encontrado")
            return False

        # Simular orden con 3000 PV (alcanza el requisito de 2930)
        pv_accumulated = 3000
        total_public_price = 5000.0

        print(f"📝 Simulando orden:")
        print(f"   PV acumulado: {pv_accumulated}")
        print(f"   Precio público total: {total_public_price} MXN")

        # Generar cashback
        cashback_id = CashbackService.generate_cashback(
            session=session,
            member_id=user.member_id,
            order_id=1,  # ID ficticio
            period_id=period.id,
            pv_accumulated=pv_accumulated,
            total_public_price=total_public_price,
            currency="MXN"
        )

        if cashback_id:
            cashback = session.get(Cashback, cashback_id)
            print(f"✅ Cashback generado exitosamente")
            print(f"   ID: {cashback_id}")
            print(f"   Descuento (70%): {cashback.discount_amount} MXN")
            print(f"   Válido hasta: {cashback.expires_at}")
            session.commit()
            return True
        else:
            print("❌ Falló la generación de cashback")
            session.rollback()
            return False


def test_loyalty_points():
    """Prueba 5: Sistema de puntos de lealtad"""
    print_header("PRUEBA 5: Sistema de Puntos de Lealtad")

    with rx.session() as session:
        user = session.query(Users).filter(Users.member_id == 1).first()
        period = session.query(Periods).first()

        if not user or not period:
            print("❌ Usuario o período no encontrado")
            return False

        # Procesar compra en día válido (día 5)
        purchase_date = datetime.now(timezone.utc).replace(day=5)

        print(f"📝 Procesando compra en día {purchase_date.day}")

        success = LoyaltyService.process_purchase(
            session=session,
            member_id=user.member_id,
            order_id=1,
            period_id=period.id,
            purchase_date=purchase_date
        )

        if success:
            summary = LoyaltyService.get_user_loyalty_summary(session, user.member_id)
            print(f"✅ Compra procesada exitosamente")
            print(f"   Puntos actuales: {summary['current_points']}/{summary['target_points']}")
            print(f"   Meses consecutivos: {summary['consecutive_months']}")
            print(f"   Estado: {summary['status']}")
            session.commit()
            return True
        else:
            print("❌ Falló el procesamiento de compra de lealtad")
            session.rollback()
            return False


def test_travel_campaign():
    """Prueba 6: Sistema de NN Travel Points"""
    print_header("PRUEBA 6: Sistema de NN Travel Points")

    with rx.session() as session:
        user = session.query(Users).filter(Users.member_id == 1).first()
        period = session.query(Periods).first()

        if not user or not period:
            print("❌ Usuario o período no encontrado")
            return False

        # Crear campaña si no existe
        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=180)  # 6 meses

        campaign_id = TravelPointsService.create_campaign(
            session=session,
            name="Campaña Test 2025",
            start_date=now,
            end_date=end_date,
            period_id=period.id,
            target_points=200,
            is_promo_active=False
        )

        if not campaign_id:
            print("⚠️  Usando campaña existente")
            campaign = TravelPointsService.get_active_campaign(session)
            if campaign:
                campaign_id = campaign.id

        # Añadir puntos por rango
        success = TravelPointsService.add_points_from_rank(
            session=session,
            member_id=user.member_id,
            rank_name="Emprendedor",
            campaign_id=campaign_id
        )

        if success:
            summary = TravelPointsService.get_user_points_summary(
                session, user.member_id, campaign_id
            )
            print(f"✅ Puntos de travel añadidos exitosamente")
            print(f"   Total de puntos: {summary['total_points']}/{summary['target_points']}")
            print(f"   Puntos por rangos propios: {summary['points_from_self_ranks']}")
            print(f"   Califica para viaje: {'Sí' if summary['qualifies_for_travel'] else 'No'}")
            session.commit()
            return True
        else:
            print("❌ Falló la adición de puntos de travel")
            session.rollback()
            return False


def main():
    """Ejecuta todas las pruebas"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "TEST DE SISTEMAS DE WALLET Y PUNTOS" + " "*23 + "║")
    print("╚" + "="*78 + "╝")

    tests = [
        ("Creación de Wallet", test_wallet_creation),
        ("Depósito de Comisión", test_commission_deposit),
        ("Transferencia Entre Usuarios", test_wallet_transfer),
        ("Generación de Cashback", test_cashback_generation),
        ("Sistema de Lealtad", test_loyalty_points),
        ("Sistema NN Travel", test_travel_campaign)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERROR en {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Resumen final
    print_header("RESUMEN DE PRUEBAS")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")

    print(f"\n📊 Resultado: {passed}/{total} pruebas pasadas")

    if passed == total:
        print("\n🎉 ¡Todos los sistemas están funcionando correctamente!")
    else:
        print(f"\n⚠️  {total - passed} pruebas fallaron. Revisar implementación.")


if __name__ == "__main__":
    main()
