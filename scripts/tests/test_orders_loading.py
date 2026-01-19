"""
Script para probar la carga de órdenes y debugging.
"""
import os
import sys

# Agregar el path del proyecto
sys.path.insert(0, '/Users/bradrez/Documents/NNProtect_new_website')

from sqlmodel import select, and_, desc
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.products import Products
from database.addresses import Addresses
from database.users import Users
import reflex as rx

def test_orders_in_db():
    """Verifica qué órdenes existen en la base de datos."""
    print("\n" + "="*80)
    print("TEST 1: Verificar órdenes en la base de datos")
    print("="*80 + "\n")

    with rx.session() as session:
        # 1. Contar total de órdenes
        total_orders = session.exec(select(Orders)).all()
        print(f"📊 Total de órdenes en BD: {len(total_orders)}")

        # 2. Contar órdenes que NO son DRAFT
        non_draft_orders = session.exec(
            select(Orders).where(Orders.status != OrderStatus.DRAFT.value)
        ).all()
        print(f"📊 Órdenes NO DRAFT: {len(non_draft_orders)}")

        # 3. Mostrar primeras 5 órdenes con detalles
        print("\n📋 Primeras 5 órdenes:")
        for i, order in enumerate(total_orders[:5], 1):
            user = session.exec(
                select(Users).where(Users.member_id == order.member_id)
            ).first()
            user_name = f"{user.first_name} {user.last_name}" if user else "Unknown"

            print(f"\n  {i}. Order ID: {order.id}")
            print(f"     Member ID: {order.member_id} ({user_name})")
            print(f"     Status: {order.status}")
            print(f"     Total: ${order.total} {order.currency}")
            print(f"     Created: {order.created_at}")
            print(f"     Payment Confirmed: {order.payment_confirmed_at}")

def test_user_member_ids():
    """Muestra los member_ids de usuarios registrados."""
    print("\n" + "="*80)
    print("TEST 2: Member IDs de usuarios registrados")
    print("="*80 + "\n")

    with rx.session() as session:
        users = session.exec(select(Users).limit(10)).all()
        print(f"📊 Total usuarios (primeros 10): {len(users)}")

        for user in users:
            print(f"\n  Member ID: {user.member_id}")
            print(f"  Nombre: {user.first_name} {user.last_name}")
            print(f"  Email: {user.email_cache}")
            print(f"  Status: {user.status}")

def test_orders_for_specific_user(member_id: int):
    """Prueba cargar órdenes para un member_id específico."""
    print("\n" + "="*80)
    print(f"TEST 3: Órdenes para member_id={member_id}")
    print("="*80 + "\n")

    with rx.session() as session:
        # Query exactamente como en OrderState
        orders_query = select(Orders).where(
            and_(
                Orders.member_id == member_id,
                Orders.status != OrderStatus.DRAFT.value
            )
        ).order_by(desc(Orders.payment_confirmed_at))

        orders = session.exec(orders_query).all()

        print(f"📊 Órdenes encontradas: {len(orders)}")

        if not orders:
            print("\n⚠️ NO se encontraron órdenes para este usuario")
            print("   Verificando si tiene órdenes DRAFT:")
            draft_orders = session.exec(
                select(Orders).where(
                    and_(
                        Orders.member_id == member_id,
                        Orders.status == OrderStatus.DRAFT.value
                    )
                )
            ).all()
            print(f"   Órdenes DRAFT: {len(draft_orders)}")
        else:
            print("\n✅ Órdenes encontradas:")
            for order in orders:
                print(f"\n  Order ID: {order.id}")
                print(f"  Status: {order.status}")
                print(f"  Total: ${order.total} {order.currency}")
                print(f"  Payment Confirmed: {order.payment_confirmed_at}")

def test_order_state_method():
    """Simula el método load_orders de OrderState."""
    print("\n" + "="*80)
    print("TEST 4: Simulación del método load_orders()")
    print("="*80 + "\n")

    # Simular un member_id de prueba
    # Primero obtener un member_id que tenga órdenes
    with rx.session() as session:
        orders = session.exec(select(Orders).limit(5)).all()
        if not orders:
            print("⚠️ No hay órdenes en la BD para probar")
            return

        test_member_id = orders[0].member_id
        print(f"🧪 Usando member_id de prueba: {test_member_id}")

        # Ejecutar la query
        orders_query = select(Orders).where(
            and_(
                Orders.member_id == test_member_id,
                Orders.status != OrderStatus.DRAFT.value
            )
        ).order_by(desc(Orders.payment_confirmed_at))

        db_orders = session.exec(orders_query).all()

        print(f"📊 Órdenes encontradas: {len(db_orders)}")

        if db_orders:
            print("\n✅ Datos de primera orden:")
            order = db_orders[0]
            print(f"  Order ID: {order.id}")
            print(f"  Member ID: {order.member_id}")
            print(f"  Status: {order.status}")
            print(f"  Total: ${order.total}")
            print(f"  Currency: {order.currency}")
            print(f"  Shipping Address ID: {order.shipping_address_id}")

            # Obtener items
            items = session.exec(
                select(OrderItems).where(OrderItems.order_id == order.id)
            ).all()
            print(f"\n  Items en esta orden: {len(items)}")

            for item in items:
                product = session.get(Products, item.product_id)
                if product:
                    print(f"    - {product.product_name} x{item.quantity}")

if __name__ == "__main__":
    print("\n🚀 Iniciando tests de carga de órdenes...\n")

    # Test 1: Verificar órdenes en BD
    test_orders_in_db()

    # Test 2: Mostrar member_ids disponibles
    test_user_member_ids()

    # Test 3: Probar con un member_id específico (puedes cambiar este valor)
    # Usa el member_id del usuario con el que estás logueado
    print("\n" + "="*80)
    member_id_input = input("Ingresa el member_id del usuario logueado (o Enter para usar el primero): ").strip()

    if member_id_input:
        test_orders_for_specific_user(int(member_id_input))

    # Test 4: Simulación del método load_orders
    test_order_state_method()

    print("\n" + "="*80)
    print("✅ Tests completados")
    print("="*80 + "\n")
