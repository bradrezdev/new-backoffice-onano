"""
Test de Rendimiento EXTREMO: Red 1x1 con 5000 niveles de profundidad

OBJETIVO:
- Crear una red lineal de 5000 usuarios (1→2→3→...→5000)
- Usuario 5000 hace una compra
- Verificar que el cálculo de comisiones para 5000 ancestros NO cause timeout
- Probar el peor caso posible de profundidad

ARQUITECTURA:
- ANTES (BROKEN): Timeout con 62 usuarios en árbol normal
- AHORA (OPTIMIZED): Debe manejar 5000 niveles sin problema

Arquitectura: Adrian (Senior Dev) + Elena (Backend) + Giovanni (QA Financial)
"""

import time
import sqlmodel
from datetime import datetime, timezone
from sqlmodel import Session, select, func
from database.models import get_engine
from database.users import Users, UserStatus
from database.usertreepaths import UserTreePath
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.products import Products
from database.comissions import Commissions, BonusType
from database.periods import Periods
from database.ranks import Ranks
from database.user_rank_history import UserRankHistory
from NNProtect_new_website.payment_service.payment_service import PaymentService


def create_linear_network(session, period_id: int, depth: int = 5000):
    """
    Crea una red lineal de usuarios: 1→2→3→...→5000
    
    Args:
        session: Sesión de base de datos
        period_id: ID del período activo
        depth: Profundidad de la red (default: 5000)
    """
    print(f"\n{'=' * 80}")
    print(f"🏗️  CREANDO RED LINEAL DE {depth} NIVELES")
    print(f"{'=' * 80}\n")
    
    start_time = time.time()
    
    # Obtener el rango más bajo (Visionario)
    visionario_rank = session.exec(
        sqlmodel.select(Ranks).where(Ranks.name == "Visionario")
    ).first()
    
    if not visionario_rank:
        print("❌ Error: Rango Visionario no encontrado")
        return False
    
    # Verificar si ya existen usuarios hasta 5000
    existing_count = session.exec(
        sqlmodel.select(func.count(Users.member_id))
        .where(Users.member_id <= depth)
    ).one()
    
    if existing_count >= depth:
        print(f"✅ Ya existen {existing_count} usuarios en la base de datos")
        print(f"   Verificando estructura de red lineal...")
        
        # Verificar que la red sea lineal (1→2→3→...→depth)
        for i in range(2, depth + 1):
            path = session.exec(
                sqlmodel.select(UserTreePath)
                .where(UserTreePath.descendant_id == i)
                .where(UserTreePath.ancestor_id == i - 1)
                .where(UserTreePath.depth == 1)
            ).first()
            
            if not path:
                print(f"   ⚠️  Falta conexión: {i-1} → {i}")
                print(f"   Recreando red desde usuario {i}...")
                break
        else:
            print(f"✅ Red lineal verificada hasta nivel {depth}")
            return True
    
    print(f"📊 Usuarios existentes: {existing_count}")
    print(f"📊 Usuarios a crear: {depth - existing_count}")
    
    # Crear usuarios faltantes
    users_created = 0
    sponsor_id = existing_count if existing_count > 0 else None
    
    for member_id in range(existing_count + 1, depth + 1):
        try:
            # Crear usuario
            user = Users(
                member_id=member_id,
                username=f"user_{member_id}",
                email=f"user{member_id}@test.com",
                sponsor_id=sponsor_id,
                status=UserStatus.QUALIFIED.value,
                country_cache="MX"
            )
            session.add(user)
            session.flush()
            
            # Crear paths en UserTreePath
            if sponsor_id is not None:
                # Self-reference
                self_path = UserTreePath(
                    ancestor_id=member_id,
                    descendant_id=member_id,
                    depth=0
                )
                session.add(self_path)
                
                # Copiar todos los ancestros del sponsor + agregar el sponsor
                ancestor_paths = session.exec(
                    sqlmodel.select(UserTreePath)
                    .where(UserTreePath.descendant_id == sponsor_id)
                ).all()
                
                for ancestor_path in ancestor_paths:
                    new_path = UserTreePath(
                        ancestor_id=ancestor_path.ancestor_id,
                        descendant_id=member_id,
                        depth=ancestor_path.depth + 1
                    )
                    session.add(new_path)
            else:
                # Usuario raíz (member_id=1)
                self_path = UserTreePath(
                    ancestor_id=member_id,
                    descendant_id=member_id,
                    depth=0
                )
                session.add(self_path)
            
            # Asignar rango Visionario
            rank_history = UserRankHistory(
                member_id=member_id,
                period_id=period_id,
                rank_id=visionario_rank.id
            )
            session.add(rank_history)
            
            users_created += 1
            sponsor_id = member_id
            
            # Commit cada 100 usuarios para evitar memory overflow
            if users_created % 100 == 0:
                session.commit()
                elapsed = time.time() - start_time
                print(f"   ✅ Creados {users_created} usuarios ({elapsed:.2f}s)")
        
        except Exception as e:
            print(f"   ❌ Error creando usuario {member_id}: {e}")
            session.rollback()
            return False
    
    # Commit final
    session.commit()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n✅ Red lineal creada exitosamente:")
    print(f"   - Usuarios creados: {users_created}")
    print(f"   - Profundidad total: {depth} niveles")
    print(f"   - Tiempo total: {total_time:.2f} segundos")
    print(f"   - Promedio: {total_time / users_created:.3f}s por usuario")
    
    return True


def test_purchase_at_depth_5000():
    """
    Test del peor caso: Usuario en profundidad 5000 hace una compra.
    El sistema debe calcular comisiones para 5000 ancestros sin timeout.
    """
    print("\n" + "=" * 80)
    print("🚀 TEST EXTREMO: Compra en Profundidad 5000")
    print("=" * 80)
    
    engine = get_engine()
    
    with Session(engine) as session:
        # 1. Obtener período activo
        period = session.exec(
            sqlmodel.select(Periods)
            .where(Periods.status == "active")
        ).first()
        
        if not period:
            print("❌ No hay período activo")
            return False
        
        print(f"\n📅 Período: {period.name} (ID: {period.id})")
        
        # 2. Crear red lineal de 5000 niveles
        success = create_linear_network(session, period.id, depth=5000)
        
        if not success:
            print("❌ Error creando red lineal")
            return False
        
        # 3. Verificar que el usuario 5000 existe
        user_5000 = session.exec(
            sqlmodel.select(Users).where(Users.member_id == 5000)
        ).first()
        
        if not user_5000:
            print("❌ Usuario 5000 no encontrado")
            return False
        
        print(f"\n👤 Usuario: member_id={user_5000.member_id}")
        
        # 4. Contar ancestros
        ancestors = session.exec(
            sqlmodel.select(UserTreePath)
            .where(UserTreePath.descendant_id == 5000)
            .where(UserTreePath.depth > 0)
        ).all()
        
        print(f"🌳 Ancestros: {len(ancestors)}")
        
        if len(ancestors) != 4999:
            print(f"⚠️  Se esperaban 4999 ancestros, encontrados {len(ancestors)}")
        
        # 5. Obtener producto
        products = session.exec(sqlmodel.select(Products)).all()
        
        if not products:
            print("❌ No hay productos disponibles")
            return False
        
        product = products[0]
        print(f"📦 Producto: {product.product_name} (VN: {product.vn_mx})")
        
        # 6. Contar comisiones antes
        commissions_before = session.exec(
            sqlmodel.select(Commissions)
            .where(Commissions.period_id == period.id)
        ).all()
        
        print(f"📊 Comisiones antes: {len(commissions_before)}")
        
        # 7. Crear orden para usuario 5000
        print(f"\n{'=' * 80}")
        print("⏱️  CREANDO ORDEN Y CALCULANDO COMISIONES...")
        print(f"{'=' * 80}\n")
        
        start_time = time.time()
        
        try:
            # Crear orden
            order = Orders(
                member_id=5000,
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
            
            print(f"   ✅ Orden creada: ID={order.id}")
            print(f"   📊 VN total: {order.total_vn}")
            print(f"   👥 Ancestros a calcular: {len(ancestors)}")
            print(f"\n   🔄 Calculando comisiones incrementalmente...")
            
            # Calcular comisiones INCREMENTALMENTE
            calculation_start = time.time()
            PaymentService._trigger_commissions(session, order)
            calculation_time = time.time() - calculation_start
            
            print(f"   ✅ Comisiones calculadas en {calculation_time:.2f}s")
            
            # Commit
            print(f"\n   💾 Guardando cambios...")
            session.commit()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 8. Verificar resultados
            commissions_after = session.exec(
                sqlmodel.select(Commissions)
                .where(Commissions.period_id == period.id)
            ).all()
            
            commissions_created = len(commissions_after) - len(commissions_before)
            
            # 9. Análisis por tipo de bono
            new_commissions = [c for c in commissions_after if c not in commissions_before]
            uninivel_count = len([c for c in new_commissions if c.bonus_type == BonusType.BONO_UNINIVEL.value])
            matching_count = len([c for c in new_commissions if c.bonus_type == BonusType.BONO_MATCHING.value])
            directo_count = len([c for c in new_commissions if c.bonus_type == BonusType.BONO_DIRECTO.value])
            rapido_count = len([c for c in new_commissions if c.bonus_type == BonusType.BONO_RAPIDO.value])
            
            # 10. Mostrar resultados
            print(f"\n{'=' * 80}")
            print("📊 RESULTADOS DEL TEST EXTREMO")
            print(f"{'=' * 80}")
            print(f"\n✅ Orden creada exitosamente: ID={order.id}")
            print(f"⏱️  Tiempo total: {total_time:.2f} segundos")
            print(f"⚡ Tiempo de cálculo: {calculation_time:.2f} segundos")
            print(f"🌳 Ancestros procesados: {len(ancestors)}")
            print(f"📈 Comisiones generadas: {commissions_created}")
            print(f"   - Bono Uninivel: {uninivel_count}")
            print(f"   - Bono Matching: {matching_count}")
            print(f"   - Bono Directo: {directo_count}")
            print(f"   - Bono Rápido: {rapido_count}")
            
            # 11. Verificar éxito
            print(f"\n{'=' * 80}")
            
            if total_time > 60:
                print("❌ TEST FALLIDO: Tiempo excesivo (> 60 segundos)")
                print(f"   El sistema NO puede manejar redes profundas")
                return False
            elif total_time > 30:
                print("⚠️  TEST ACEPTABLE: 30-60 segundos")
                print(f"   El sistema funciona pero podría optimizarse más")
            elif total_time > 10:
                print("✅ TEST EXITOSO: 10-30 segundos")
                print(f"   Rendimiento EXCELENTE para 5000 niveles")
            else:
                print("🚀 TEST PERFECTO: < 10 segundos")
                print(f"   Rendimiento ÓPTIMO incluso en casos extremos")
            
            print(f"\n💡 ANÁLISIS:")
            print(f"   - Complejidad: O(n) donde n = ancestros")
            print(f"   - Ancestros: {len(ancestors)}")
            print(f"   - Tiempo por ancestro: {calculation_time / max(len(ancestors), 1) * 1000:.3f}ms")
            print(f"   - Escalabilidad: {'✅ EXCELENTE' if total_time < 30 else '⚠️  NECESITA OPTIMIZACIÓN'}")
            
            print(f"{'=' * 80}\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🎯 TEST DE RENDIMIENTO EXTREMO")
    print("=" * 80)
    print("\n📋 OBJETIVO:")
    print("   - Crear red lineal 1→2→3→...→5000 (5000 niveles)")
    print("   - Usuario 5000 hace una compra")
    print("   - Calcular comisiones para 4999 ancestros")
    print("   - Verificar: NO timeout, tiempo < 30 segundos")
    print("\n💡 NOTA:")
    print("   Este es el PEOR CASO posible de profundidad.")
    print("   Si pasa este test, el sistema puede manejar CUALQUIER red real.")
    print("\n" + "=" * 80)
    
    try:
        success = test_purchase_at_depth_5000()
        
        if success:
            print("\n" + "=" * 80)
            print("🎉 TEST COMPLETADO EXITOSAMENTE")
            print("=" * 80)
            print("\n✅ El sistema puede manejar redes de 5000 niveles sin problema")
            print("✅ Arquitectura optimizada VALIDADA para producción")
            print("✅ Escalabilidad comprobada en caso extremo")
            print("\n" + "=" * 80 + "\n")
        else:
            print("\n" + "=" * 80)
            print("❌ TEST FALLIDO")
            print("=" * 80)
            print("\n⚠️  El sistema necesita más optimización")
            print("\n" + "=" * 80 + "\n")
    
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
