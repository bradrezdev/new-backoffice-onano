"""
Script simple para verificar las órdenes creadas usando SQL directo.
"""
from sqlalchemy import create_engine, text

# Conexión a la base de datos
db_url = "postgresql://postgres.wxjknxpyqgxxjtrkuyev:nn_backoffice!@aws-1-us-east-2.pooler.supabase.com:6543/postgres"
engine = create_engine(db_url)

def verify_orders():
    """Verifica las órdenes creadas para usuarios 8, 9, 10"""
    print("\n" + "="*80)
    print("VERIFICACIÓN DE ÓRDENES CREADAS")
    print("="*80 + "\n")

    with engine.connect() as conn:
        # Verificar órdenes para cada usuario
        for member_id in [8, 9, 10]:
            print(f"\n👤 Usuario member_id={member_id}:")

            # Query que simula exactamente lo que hace OrderState.load_orders()
            result = conn.execute(text("""
                SELECT
                    o.id,
                    o.status,
                    o.total,
                    o.total_pv,
                    o.payment_confirmed_at,
                    o.created_at,
                    u.first_name,
                    u.last_name
                FROM orders o
                LEFT JOIN users u ON o.member_id = u.member_id
                WHERE o.member_id = :mid
                  AND o.status != 'draft'
                ORDER BY o.payment_confirmed_at DESC
            """), {"mid": member_id})

            orders = list(result)

            if not orders:
                print(f"   ❌ No se encontraron órdenes NO-DRAFT")

                # Verificar si hay órdenes draft
                result_draft = conn.execute(text("""
                    SELECT COUNT(*) FROM orders
                    WHERE member_id = :mid AND status = 'draft'
                """), {"mid": member_id})
                draft_count = result_draft.scalar()
                if draft_count:
                    print(f"   ⚠️  Tiene {draft_count} órdenes DRAFT")
            else:
                print(f"   ✅ {len(orders)} órdenes encontradas:")
                for order in orders:
                    print(f"\n      Order ID: {order[0]}")
                    print(f"      Status: {order[1]}")
                    print(f"      Total: ${order[2]}")
                    print(f"      Total PV: {order[3]}")
                    print(f"      Payment Confirmed: {order[4]}")
                    print(f"      Usuario: {order[6]} {order[7]}")

                    # Contar items
                    items_result = conn.execute(text("""
                        SELECT COUNT(*) FROM orderitems WHERE order_id = :oid
                    """), {"oid": order[0]})
                    item_count = items_result.scalar()
                    print(f"      Items: {item_count} productos")

        print("\n" + "="*80)
        print("RESUMEN TOTAL")
        print("="*80 + "\n")

        # Total general
        result = conn.execute(text("""
            SELECT
                COUNT(*) as total_orders,
                SUM(total) as total_revenue,
                SUM(total_pv) as total_pv
            FROM orders
            WHERE member_id IN (8, 9, 10)
              AND status = 'payment_confirmed'
        """))

        summary = result.first()
        print(f"📊 Órdenes confirmadas: {summary[0]}")
        print(f"💰 Revenue total: ${summary[1]}")
        print(f"🎯 PV total: {summary[2]}")
        print()

if __name__ == "__main__":
    verify_orders()
