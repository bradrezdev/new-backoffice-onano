"""
Test E2E del flujo completo de pago con wallet virtual.

Flujo testeado:
1. Crear usuario con wallet y balance
2. Crear orden en estado PENDING_PAYMENT
3. Procesar pago con wallet
4. Verificar actualización de PV/PVG
5. Verificar generación de comisiones
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import reflex as rx
from datetime import datetime, timezone
from NNProtect_new_website.payment_service.payment_service import PaymentService
from NNProtect_new_website.mlm_service.wallet_service import WalletService
from NNProtect_new_website.mlm_service.rank_service import RankService
from NNProtect_new_website.mlm_service.genealogy_service import GenealogyService
from database.users import Users
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.products import Products
from database.wallet import Wallets
from database.comissions import Commissions
from database.periods import Periods


def test_wallet_payment_flow():
    """Test completo del flujo de pago con wallet"""

    print("\n" + "="*80)
    print("TEST E2E: Flujo de Pago con Wallet Virtual")
    print("="*80 + "\n")

    with rx.session() as session:
        try:
            # ============================================================
            # PASO 1: Crear estructura de red (sponsor -> buyer)
            # ============================================================
            print("📋 PASO 1: Creando estructura de red...")

            # Crear sponsor
            sponsor = Users(
                member_id=9001,
                first_name="Sponsor",
                last_name="Test",
                email_cache="sponsor@test.com",
                country_cache="MX",
                pv_cache=0,
                pvg_cache=0
            )
            session.add(sponsor)
            session.flush()

            # Crear buyer (comprador)
            buyer = Users(
                member_id=9002,
                first_name="Buyer",
                last_name="Test",
                email_cache="buyer@test.com",
                country_cache="MX",
                sponsor_id=9001,
                pv_cache=0,
                pvg_cache=0
            )
            session.add(buyer)
            session.flush()

            # Crear genealogía
            GenealogyService.add_member_to_tree(session, 9002, 9001)

            print(f"✅ Sponsor creado: member_id={sponsor.member_id}")
            print(f"✅ Buyer creado: member_id={buyer.member_id}")

            # ============================================================
            # PASO 2: Crear wallet para buyer con balance
            # ============================================================
            print("\n📋 PASO 2: Creando wallet con balance...")

            wallet_id = WalletService.create_wallet(
                session=session,
                member_id=buyer.member_id,
                currency="MXN"
            )

            # Depositar balance inicial
            wallet = session.get(Wallets, wallet_id)
            wallet.balance = 5000.0  # 5000 MXN
            session.add(wallet)
            session.flush()

            print(f"✅ Wallet creada: ID={wallet_id}, Balance={wallet.balance} MXN")

            # ============================================================
            # PASO 3: Crear producto de prueba
            # ============================================================
            print("\n📋 PASO 3: Creando producto de prueba...")

            # Verificar si existe producto, si no crearlo
            import sqlmodel
            product = session.exec(
                sqlmodel.select(Products).where(Products.id == 1)
            ).first()

            if not product:
                product = Products(
                    id=1,
                    product_name="Suplemento Test",
                    SKU="TEST-001",
                    description="Producto de prueba",
                    presentation="líquido",
                    type="suplemento",
                    pv_mx=100,
                    vn_mx=50.0,
                    price_mx=100.0
                )
                session.add(product)
                session.flush()

            print(f"✅ Producto: {product.product_name}, PV={product.pv_mx}, VN={product.vn_mx}")

            # ============================================================
            # PASO 4: Crear orden en estado PENDING_PAYMENT
            # ============================================================
            print("\n📋 PASO 4: Creando orden PENDING_PAYMENT...")

            order = Orders(
                member_id=buyer.member_id,
                country="MX",
                currency="MXN",
                subtotal=200.0,
                shipping_cost=0.0,
                tax=0.0,
                discount=0.0,
                total=200.0,
                total_pv=200,  # 2 productos x 100 PV
                total_vn=100.0,  # 2 productos x 50 VN
                status=OrderStatus.PENDING_PAYMENT.value
            )
            session.add(order)
            session.flush()

            # Agregar items a la orden
            order_item = OrderItems(
                order_id=order.id,
                product_id=product.id,
                quantity=2,
                unit_price=100.0,
                unit_pv=100,
                unit_vn=50.0,
                line_total=200.0,
                line_pv=200,
                line_vn=100.0
            )
            session.add(order_item)
            session.flush()

            print(f"✅ Orden creada: ID={order.id}")
            print(f"   Total: {order.total} MXN")
            print(f"   PV: {order.total_pv}")
            print(f"   VN: {order.total_vn}")

            # ============================================================
            # PASO 5: Crear período actual
            # ============================================================
            print("\n📋 PASO 5: Verificando período actual...")

            current_period = session.exec(
                sqlmodel.select(Periods).where(Periods.closed_at == None)
            ).first()

            if not current_period:
                from NNProtect_new_website.utils.timezone_mx import get_mexico_now
                now = get_mexico_now()

                current_period = Periods(
                    name=f"Test Period {now.strftime('%Y-%m')}",
                    starts_on=now.replace(day=1, hour=0, minute=0, second=0),
                    ends_on=now.replace(day=28, hour=23, minute=59, second=59)
                )
                session.add(current_period)
                session.flush()
                print(f"✅ Período creado: {current_period.name}")
            else:
                print(f"✅ Período actual: {current_period.name}")

            # ============================================================
            # PASO 6: Procesar pago con wallet
            # ============================================================
            print("\n📋 PASO 6: Procesando pago con wallet...")
            print(f"   Balance antes: {wallet.balance} MXN")

            result = PaymentService.process_wallet_payment(
                session=session,
                order_id=order.id,
                member_id=buyer.member_id
            )

            if not result["success"]:
                print(f"❌ ERROR: {result['message']}")
                return False

            print(f"✅ {result['message']}")

            # ============================================================
            # PASO 7: Verificar estado de la orden
            # ============================================================
            print("\n📋 PASO 7: Verificando estado de orden...")

            session.refresh(order)

            print(f"   Estado: {order.status}")
            print(f"   Payment confirmed at: {order.payment_confirmed_at}")
            print(f"   Period ID: {order.period_id}")
            print(f"   Payment method: {order.payment_method}")

            assert order.status == OrderStatus.PAYMENT_CONFIRMED.value, "Estado incorrecto"
            assert order.payment_confirmed_at is not None, "Timestamp faltante"
            assert order.period_id is not None, "Period ID faltante"
            assert order.payment_method == "wallet", "Método de pago incorrecto"

            print("✅ Orden confirmada correctamente")

            # ============================================================
            # PASO 8: Verificar balance de wallet
            # ============================================================
            print("\n📋 PASO 8: Verificando balance de wallet...")

            session.refresh(wallet)

            expected_balance = 5000.0 - 200.0  # Balance inicial - total orden

            print(f"   Balance después: {wallet.balance} MXN")
            print(f"   Balance esperado: {expected_balance} MXN")

            assert wallet.balance == expected_balance, f"Balance incorrecto: {wallet.balance} != {expected_balance}"

            print("✅ Balance actualizado correctamente")

            # ============================================================
            # PASO 9: Verificar actualización de PV/PVG
            # ============================================================
            print("\n📋 PASO 9: Verificando actualización de PV/PVG...")

            session.refresh(buyer)
            session.refresh(sponsor)

            print(f"   Buyer PV: {buyer.pv_cache} (esperado: 200)")
            print(f"   Buyer PVG: {buyer.pvg_cache} (esperado: 200)")
            print(f"   Sponsor PVG: {sponsor.pvg_cache} (esperado: 200)")

            assert buyer.pv_cache == 200, f"PV del buyer incorrecto: {buyer.pv_cache}"
            assert buyer.pvg_cache == 200, f"PVG del buyer incorrecto: {buyer.pvg_cache}"
            assert sponsor.pvg_cache == 200, f"PVG del sponsor incorrecto: {sponsor.pvg_cache}"

            print("✅ PV/PVG actualizados correctamente")

            # ============================================================
            # PASO 10: Verificar generación de comisiones
            # ============================================================
            print("\n📋 PASO 10: Verificando comisiones generadas...")

            commissions = session.exec(
                sqlmodel.select(Commissions).where(
                    Commissions.source_order_id == order.id
                )
            ).all()

            print(f"   Comisiones generadas: {len(commissions)}")

            for comm in commissions:
                print(f"   - {comm.bonus_type}: {comm.amount_converted} {comm.currency_destination} para member_id={comm.member_id}")

            # Debe haber al menos Bono Directo
            assert len(commissions) > 0, "No se generaron comisiones"

            print("✅ Comisiones generadas correctamente")

            # ============================================================
            # PASO 11: Rollback (no guardar datos de prueba)
            # ============================================================
            print("\n📋 PASO 11: Limpiando datos de prueba...")
            session.rollback()
            print("✅ Rollback completado")

            # ============================================================
            # RESUMEN
            # ============================================================
            print("\n" + "="*80)
            print("✅ TEST COMPLETADO EXITOSAMENTE")
            print("="*80)
            print("\nResumen:")
            print(f"  • Orden procesada: ID={order.id}")
            print(f"  • Estado final: {order.status}")
            print(f"  • Wallet debitada: 200 MXN")
            print(f"  • PV actualizado: Buyer={buyer.pv_cache}, Sponsor PVG={sponsor.pvg_cache}")
            print(f"  • Comisiones generadas: {len(commissions)}")
            print("\n")

            return True

        except Exception as e:
            print(f"\n❌ ERROR EN TEST: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return False


if __name__ == "__main__":
    success = test_wallet_payment_flow()
    sys.exit(0 if success else 1)
