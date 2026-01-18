"""
Test script para validar OrderState
Verifica que las órdenes se cargan correctamente desde la base de datos.
"""

import sys
from datetime import datetime, timezone
from sqlmodel import select, Session
from database.engine_config import get_engine
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.products import Products
from database.addresses import Addresses
from database.users_addresses import UserAddresses
from database.users import Users

def test_database_orders():
    """Verifica que hay órdenes en la base de datos"""
    print("\n" + "="*80)
    print("TEST 1: Verificar órdenes en la base de datos")
    print("="*80)

    engine = get_engine()

    with Session(engine) as session:
        # Contar todas las órdenes
        total_orders = session.exec(
            select(Orders)
        ).all()

        print(f"\n📊 Total de órdenes en BD: {len(total_orders)}")

        # Contar órdenes por estado
        for status in OrderStatus:
            count = len([o for o in total_orders if o.status == status.value])
            print(f"  - {status.value}: {count}")

        # Órdenes que NO son DRAFT (las que se deben mostrar)
        non_draft_orders = [o for o in total_orders if o.status != OrderStatus.DRAFT.value]
        print(f"\n✅ Órdenes a mostrar (no DRAFT): {len(non_draft_orders)}")

        if non_draft_orders:
            print("\n📋 Primeras 5 órdenes:")
            for order in non_draft_orders[:5]:
                print(f"\n  Order ID: {order.id}")
                print(f"    Member ID: {order.member_id}")
                print(f"    Status: {order.status}")
                print(f"    Total: {order.currency} {order.total}")
                print(f"    Created: {order.created_at}")
                print(f"    Payment Confirmed: {order.payment_confirmed_at}")

                # Verificar address
                if order.shipping_address_id:
                    address = session.exec(
                        select(Addresses).where(Addresses.id == order.shipping_address_id)
                    ).first()
                    if address:
                        print(f"    Address: {address.street}, {address.city}, {address.state}")

                # Verificar productos
                items = session.exec(
                    select(OrderItems).where(OrderItems.order_id == order.id)
                ).all()
                print(f"    Products: {len(items)} items")

                for item in items:
                    product = session.exec(
                        select(Products).where(Products.id == item.product_id)
                    ).first()
                    if product:
                        print(f"      - {product.product_name} x{item.quantity}")
        else:
            print("\n⚠️ No hay órdenes para mostrar (todas están en DRAFT)")

        return len(non_draft_orders)


def test_order_formatting():
    """Verifica que el formateo de órdenes funciona correctamente"""
    print("\n" + "="*80)
    print("TEST 2: Verificar formateo de órdenes")
    print("="*80)

    engine = get_engine()

    with Session(engine) as session:
        # Obtener una orden de prueba
        order = session.exec(
            select(Orders).where(Orders.status != OrderStatus.DRAFT.value)
        ).first()

        if not order:
            print("\n⚠️ No hay órdenes disponibles para testing")
            return False

        print(f"\n🔍 Testeando orden ID: {order.id}")

        # Formatear fecha
        from NNProtect_new_website.utils.timezone_mx import format_mexico_date, convert_to_mexico_time

        if order.payment_confirmed_at:
            mexico_dt = convert_to_mexico_time(order.payment_confirmed_at)
            formatted_date = format_mexico_date(mexico_dt)
            print(f"✅ Fecha formateada: {formatted_date}")

        # Formatear moneda
        def format_currency(amount: float, currency: str = "MXN") -> str:
            symbols = {"MXN": "$", "USD": "$", "COP": "$"}
            symbol = symbols.get(currency, "$")
            formatted = f"{amount:,.2f}"
            return f"{symbol}{formatted}"

        formatted_total = format_currency(order.total, order.currency)
        print(f"✅ Total formateado: {formatted_total}")

        # Mapear estado
        status_map = {
            OrderStatus.DRAFT.value: "Pendiente",
            OrderStatus.PENDING_PAYMENT.value: "Pendiente",
            OrderStatus.PAYMENT_CONFIRMED.value: "En proceso",
            OrderStatus.PROCESSING.value: "En proceso",
            OrderStatus.SHIPPED.value: "Enviado",
            OrderStatus.DELIVERED.value: "Entregado",
            OrderStatus.CANCELLED.value: "Cancelado",
            OrderStatus.REFUNDED.value: "Cancelado"
        }
        status_display = status_map.get(order.status, "Pendiente")
        print(f"✅ Estado mapeado: {order.status} -> {status_display}")

        # Verificar dirección
        if order.shipping_address_id:
            address = session.exec(
                select(Addresses).where(Addresses.id == order.shipping_address_id)
            ).first()
            if address:
                shipping_address_str = f"{address.street}, {address.city}, {address.state}"
                print(f"✅ Dirección formateada: {shipping_address_str}")

                # Verificar alias
                user_address = session.exec(
                    select(UserAddresses).where(UserAddresses.address_id == address.id)
                ).first()
                if user_address and user_address.address_name:
                    print(f"✅ Alias: {user_address.address_name}")

        # Verificar productos
        items = session.exec(
            select(OrderItems).where(OrderItems.order_id == order.id)
        ).all()

        print(f"\n📦 Productos ({len(items)} items):")
        for item in items:
            product = session.exec(
                select(Products).where(Products.id == item.product_id)
            ).first()
            if product:
                print(f"  - {product.product_name} x{item.quantity}")

        return True


def test_user_orders():
    """Verifica órdenes por usuario"""
    print("\n" + "="*80)
    print("TEST 3: Verificar órdenes por usuario")
    print("="*80)

    engine = get_engine()

    with Session(engine) as session:
        # Obtener usuarios con órdenes
        users_with_orders = session.exec(
            select(Users.member_id).distinct().join(
                Orders, Orders.member_id == Users.member_id
            ).where(Orders.status != OrderStatus.DRAFT.value)
        ).all()

        print(f"\n👥 Usuarios con órdenes: {len(users_with_orders)}")

        if users_with_orders:
            # Mostrar detalles del primer usuario
            member_id = users_with_orders[0]
            print(f"\n🔍 Detalles para member_id: {member_id}")

            user_orders = session.exec(
                select(Orders).where(
                    Orders.member_id == member_id,
                    Orders.status != OrderStatus.DRAFT.value
                )
            ).all()

            print(f"  Total de órdenes: {len(user_orders)}")

            for order in user_orders[:3]:
                print(f"\n  Order #{order.id}")
                print(f"    Status: {order.status}")
                print(f"    Total: {order.currency} {order.total}")
                print(f"    Date: {order.payment_confirmed_at}")

        return len(users_with_orders)


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*80)
    print("🧪 SUITE DE TESTS PARA ORDER STATE")
    print("="*80)

    try:
        # Test 1: Verificar base de datos
        total_orders = test_database_orders()

        # Test 2: Verificar formateo
        if total_orders > 0:
            test_order_formatting()

        # Test 3: Verificar órdenes por usuario
        test_user_orders()

        print("\n" + "="*80)
        print("✅ TESTS COMPLETADOS")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
