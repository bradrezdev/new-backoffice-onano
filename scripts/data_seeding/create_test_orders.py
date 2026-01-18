"""
Script para crear órdenes de prueba usando la lógica de admin_state.py
"""
import sys
sys.path.insert(0, '/Users/bradrez/Documents/NNProtect_new_website')

from sqlalchemy import create_engine, text
from datetime import datetime, timezone

# Conexión a la base de datos
db_url = "postgresql://postgres.wxjknxpyqgxxjtrkuyev:nn_backoffice!@aws-1-us-east-2.pooler.supabase.com:6543/postgres"
engine = create_engine(db_url)

def create_orders_for_users():
    """Crea órdenes de prueba para usuarios 8, 9, 10"""
    print("\n" + "="*80)
    print("CREANDO ÓRDENES DE PRUEBA")
    print("="*80 + "\n")

    member_ids = [8, 9, 10]
    orders_per_user = 2  # 2 órdenes por usuario

    with engine.connect() as conn:
        # 1. Obtener período actual
        result = conn.execute(text("SELECT id FROM periods ORDER BY id DESC LIMIT 1"))
        period_row = result.first()

        if not period_row:
            print("❌ No hay período activo en la BD")
            return

        period_id = period_row[0]
        print(f"✅ Período activo: {period_id}")

        # 2. Obtener productos (IDs 2-6)
        result = conn.execute(text("""
            SELECT id, product_name, price_mx, pv_mx, vn_mx
            FROM products
            WHERE id BETWEEN 2 AND 6
            ORDER BY id
            LIMIT 5
        """))

        products = list(result)

        if len(products) < 5:
            print(f"❌ Solo se encontraron {len(products)} productos (se necesitan 5)")
            return

        print(f"\n✅ Productos a usar:")
        for p in products:
            print(f"   - ID {p[0]}: {p[1]} (${p[2]}, {p[3]} PV)")

        # 3. Crear órdenes para cada usuario
        total_orders = 0

        for member_id in member_ids:
            # Verificar que el usuario existe
            result = conn.execute(text("""
                SELECT member_id, first_name, last_name, country_cache
                FROM users
                WHERE member_id = :mid
            """), {"mid": member_id})

            user = result.first()

            if not user:
                print(f"\n⚠️  Usuario member_id={member_id} no existe, saltando...")
                continue

            print(f"\n👤 Usuario: {user[1]} {user[2]} (member_id={user[0]})")

            # Crear órdenes para este usuario
            for i in range(orders_per_user):
                # Calcular totales
                subtotal = sum(p[2] for p in products)  # price_mx
                total_pv = sum(p[3] for p in products)  # pv_mx
                total_vn = sum(p[4] for p in products)  # vn_mx

                # Crear orden
                result = conn.execute(text("""
                    INSERT INTO orders (
                        member_id, country, currency, subtotal, shipping_cost,
                        tax, discount, total, total_pv, total_vn, status,
                        period_id, payment_method, created_at, payment_confirmed_at
                    )
                    VALUES (
                        :member_id, :country, 'MXN', :subtotal, 0.0,
                        0.0, 0.0, :total, :total_pv, :total_vn, 'payment_confirmed',
                        :period_id, 'admin_test', :created_at, :payment_confirmed_at
                    )
                    RETURNING id
                """), {
                    "member_id": member_id,
                    "country": user[3] or "Mexico",
                    "subtotal": subtotal,
                    "total": subtotal,
                    "total_pv": total_pv,
                    "total_vn": total_vn,
                    "period_id": period_id,
                    "created_at": datetime.now(timezone.utc),
                    "payment_confirmed_at": datetime.now(timezone.utc)
                })

                order_id = result.scalar()
                print(f"   ✅ Orden #{order_id} creada (${subtotal}, {total_pv} PV)")

                # Crear order items para cada producto
                for product in products:
                    conn.execute(text("""
                        INSERT INTO orderitems (
                            order_id, product_id, quantity, unit_price,
                            unit_pv, unit_vn, line_total, line_pv, line_vn
                        )
                        VALUES (
                            :order_id, :product_id, 1, :unit_price,
                            :unit_pv, :unit_vn, :line_total, :line_pv, :line_vn
                        )
                    """), {
                        "order_id": order_id,
                        "product_id": product[0],  # id
                        "unit_price": product[2],  # price_mx
                        "unit_pv": product[3],     # pv_mx
                        "unit_vn": product[4],     # vn_mx
                        "line_total": product[2],  # price_mx * 1
                        "line_pv": product[3],     # pv_mx * 1
                        "line_vn": product[4]      # vn_mx * 1
                    })

                total_orders += 1

        # Commit
        conn.commit()

        print(f"\n" + "="*80)
        print(f"✅ COMPLETADO: {total_orders} órdenes creadas exitosamente")
        print("="*80 + "\n")

        # Verificar órdenes creadas
        print("📋 Verificación:")
        result = conn.execute(text("""
            SELECT o.id, o.member_id, u.first_name, u.last_name, o.total, o.total_pv, o.status
            FROM orders o
            LEFT JOIN users u ON o.member_id = u.member_id
            WHERE o.member_id IN (8, 9, 10)
            AND o.status = 'payment_confirmed'
            ORDER BY o.id DESC
        """))

        for row in result:
            print(f"   Orden #{row[0]}: {row[2]} {row[3]} (member_id={row[1]}) - ${row[4]}, {row[5]} PV - {row[6]}")

if __name__ == "__main__":
    create_orders_for_users()
