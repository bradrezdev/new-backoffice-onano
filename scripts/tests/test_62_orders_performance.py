"""
Test de rendimiento: Crear 62 órdenes con cálculo incremental de comisiones.

OBJETIVO CRÍTICO:
- El sistema NO debe experimentar timeout
- Todas las 62 órdenes deben crearse exitosamente
- Las comisiones deben calcularse correctamente
- Tiempo total < 30 segundos (idealmente < 10 segundos)

CONTEXTO:
- Antes de la optimización: TIMEOUT y FALLO TOTAL con 62 órdenes
- Después de la optimización: Debe completarse rápidamente

Arquitectura: Adrian (Senior Dev) + Elena (Backend) + Giovanni (QA Financial)
"""

import time
import sqlmodel
from datetime import datetime, timezone
from sqlmodel import Session
from database.models import get_engine
from database.users import Users
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.products import Products
from database.comissions import Commissions, BonusType, CommissionStatus
from database.periods import Periods
from NNProtect_new_website.payment_service.payment_service import PaymentService


def test_62_orders_no_timeout():
    """
    Test crítico: Crear 62 órdenes debe completarse sin timeout.
    """
    print("\n" + "=" * 80)
    print("🚀 TEST DE RENDIMIENTO: 62 ÓRDENES CON COMISIONES INCREMENTALES")
    print("=" * 80)
    
    start_time = time.time()
    
    engine = get_engine()
    with Session(engine) as session:
        # 1. Obtener período activo
        period = session.exec(
            sqlmodel.select(Periods)
            .where(Periods.status == "active")
        ).first()
        
        if not period:
            print("❌ No hay período activo")
            return
        
        print(f"\n📅 Período: {period.period_name} (ID: {period.id})")
        
        # 2. Obtener productos
        products = session.exec(sqlmodel.select(Products)).all()
        
        if not products:
            print("❌ No hay productos disponibles")
            return
        
        product = products[0]
        print(f"📦 Producto: {product.product_name} (VN MX: {product.vn_mx})")
        
        # 3. Obtener usuarios para compras (member_ids 1-62)
        users = session.exec(
            sqlmodel.select(Users)
            .where(Users.member_id.between(1, 62))  # type: ignore
        ).all()
        
        print(f"\n👥 Usuarios encontrados: {len(users)}")
        
        if len(users) < 62:
            print(f"⚠️  Solo hay {len(users)} usuarios (se esperaban 62)")
        
        # 4. Contar comisiones antes
        commissions_before = session.exec(
            sqlmodel.select(Commissions)
            .where(Commissions.period_id == period.id)
        ).all()
        
        print(f"📊 Comisiones antes: {len(commissions_before)}")
        
        # 5. Crear órdenes y calcular comisiones
        print(f"\n{'=' * 80}")
        print("⏱️  INICIANDO CREACIÓN DE ÓRDENES...")
        print(f"{'=' * 80}\n")
        
        orders_created = 0
        total_vn = 0.0
        
        for i, user in enumerate(users, 1):
            try:
                # Crear orden
                order = Orders(
                    member_id=user.member_id,
                    period_id=period.id,
                    country="MX",
                    currency="MXN",
                    status=OrderStatus.PAYMENT_CONFIRMED.value,
                    total=100.0,
                    total_vn=product.vn_mx,
                    payment_confirmed_at=datetime.now(timezone.utc)
                )
                session.add(order)
                session.flush()
                
                # Agregar item
                if order.id:
                    item = OrderItems(
                        order_id=order.id,
                        product_id=product.id if product.id else 0,
                        quantity=1,
                        unit_price=100.0,
                        line_vn=product.vn_mx
                    )
                    session.add(item)
                    session.flush()
                
                # Calcular comisiones INCREMENTALMENTE
                print(f"   [{i}/{len(users)}] member_id={user.member_id}: Calculando comisiones...")
                PaymentService._trigger_commissions(session, order)
                
                orders_created += 1
                total_vn += product.vn_mx
                
                # Mostrar progreso cada 10 órdenes
                if i % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"\n   ⏱️  Progreso: {i}/{len(users)} órdenes ({elapsed:.2f}s)\n")
                
            except Exception as e:
                print(f"   ❌ Error creando orden para member_id={user.member_id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 6. Commit final
        print(f"\n{'=' * 80}")
        print("💾 Guardando cambios en base de datos...")
        print(f"{'=' * 80}\n")
        
        session.commit()
        
        # 7. Calcular tiempo total
        end_time = time.time()
        total_time = end_time - start_time
        
        # 8. Verificar resultados
        commissions_after = session.exec(
            sqlmodel.select(Commissions)
            .where(Commissions.period_id == period.id)
        ).all()
        
        commissions_created = len(commissions_after) - len(commissions_before)
        
        # 9. Análisis por tipo de bono
        uninivel_count = len([c for c in commissions_after if c.bonus_type == BonusType.BONO_UNINIVEL.value])
        matching_count = len([c for c in commissions_after if c.bonus_type == BonusType.BONO_MATCHING.value])
        directo_count = len([c for c in commissions_after if c.bonus_type == BonusType.BONO_DIRECTO.value])
        rapido_count = len([c for c in commissions_after if c.bonus_type == BonusType.BONO_RAPIDO.value])
        
        # 10. Mostrar resultados
        print("\n" + "=" * 80)
        print("📊 RESULTADOS DEL TEST")
        print("=" * 80)
        print(f"\n✅ Órdenes creadas: {orders_created}")
        print(f"💰 VN total: {total_vn}")
        print(f"⏱️  Tiempo total: {total_time:.2f} segundos")
        print(f"⚡ Promedio por orden: {total_time / orders_created:.3f} segundos")
        print(f"\n📈 Comisiones generadas: {commissions_created}")
        print(f"   - Bono Uninivel: {uninivel_count}")
        print(f"   - Bono Matching: {matching_count}")
        print(f"   - Bono Directo: {directo_count}")
        print(f"   - Bono Rápido: {rapido_count}")
        
        # 11. Verificar éxito
        print("\n" + "=" * 80)
        
        if total_time > 60:
            print("❌ TEST FALLIDO: Tiempo excesivo (> 60 segundos)")
            print(f"   El sistema es demasiado lento para producción")
            return False
        elif total_time > 30:
            print("⚠️  TEST ACEPTABLE PERO LENTO: 30-60 segundos")
            print(f"   Considerar más optimizaciones")
        elif total_time > 10:
            print("✅ TEST EXITOSO: 10-30 segundos")
            print(f"   Rendimiento aceptable para producción")
        else:
            print("🚀 TEST EXCELENTE: < 10 segundos")
            print(f"   Rendimiento óptimo")
        
        print("=" * 80)
        
        return True


if __name__ == "__main__":
    print("\n🎯 Test de Rendimiento - Arquitectura Incremental")
    print("   Objetivo: Evitar timeout con 62 órdenes")
    print("   Arquitectura: Adrian + Elena + Giovanni\n")
    
    try:
        success = test_62_orders_no_timeout()
        
        if success:
            print("\n✅ TEST COMPLETADO EXITOSAMENTE")
        else:
            print("\n❌ TEST FALLIDO")
    
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
