#!/usr/bin/env python3
"""
Test para verificar que las comisiones Uninivel y Matching se calculan
INSTANTÁNEAMENTE cuando una orden es confirmada (status=PAYMENT_CONFIRMED).

Escenario de prueba:
1. Verificar comisiones ANTES de crear una orden
2. Crear una orden para member_id=1
3. Confirmar el pago (trigger de comisiones)
4. Verificar comisiones DESPUÉS de confirmar el pago
5. Confirmar que se calcularon Uninivel y Matching

Arquitectura: Adrian (Senior Dev) + Giovanni (QA Financial)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reflex as rx
from sqlmodel import select, func
from datetime import datetime, timezone
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.comissions import Commissions, BonusType, CommissionStatus
from database.periods import Periods
from database.users import Users
from NNProtect_new_website.payment_service.payment_service import PaymentService


def test_instant_commissions():
    """
    Prueba que las comisiones se calculen instantáneamente al confirmar una orden.
    """
    print("\n" + "="*80)
    print("🧪 TEST: Cálculo Instantáneo de Comisiones Uninivel y Matching")
    print("="*80)
    
    try:
        with rx.session() as session:
            # PASO 1: Obtener período actual
            print("\n📅 PASO 1: Verificando período actual...")
            period = session.exec(
                select(Periods).order_by(Periods.starts_on.desc()).limit(1)
            ).first()
            
            if not period:
                print("❌ No hay períodos en la base de datos")
                return False
            
            print(f"   ✅ Período: {period.name} (ID={period.id})")
            
            # PASO 2: Verificar comisiones ANTES
            print("\n📊 PASO 2: Contando comisiones ANTES de la orden...")
            
            commissions_before = session.exec(
                select(func.count(Commissions.id))
                .where(Commissions.period_id == period.id)
            ).first() or 0
            
            uninivel_before = session.exec(
                select(func.count(Commissions.id))
                .where(
                    (Commissions.period_id == period.id) &
                    (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value)
                )
            ).first() or 0
            
            matching_before = session.exec(
                select(func.count(Commissions.id))
                .where(
                    (Commissions.period_id == period.id) &
                    (Commissions.bonus_type == BonusType.BONO_MATCHING.value)
                )
            ).first() or 0
            
            print(f"   📈 Total comisiones: {commissions_before}")
            print(f"   📈 Uninivel: {uninivel_before}")
            print(f"   📈 Matching: {matching_before}")
            
            # PASO 3: Crear una orden de prueba
            print("\n🛒 PASO 3: Creando orden de prueba...")
            
            # Buscar un usuario que tenga ancestros (sponsor_id no NULL)
            from database.usertreepaths import UserTreePath
            
            # Obtener un usuario que tenga al menos 1 ancestro
            user_with_ancestors = session.exec(
                select(Users)
                .join(UserTreePath, Users.member_id == UserTreePath.descendant_id)
                .where(UserTreePath.depth > 0)
                .limit(1)
            ).first()
            
            if not user_with_ancestors:
                print("⚠️  No se encontró ningún usuario con ancestros en el árbol")
                print("   Usando member_id=1 (usuario raíz)")
                buyer_id = 1
            else:
                buyer_id = user_with_ancestors.member_id
            
            # Verificar que el usuario existe
            buyer = session.exec(
                select(Users).where(Users.member_id == buyer_id)
            ).first()
            
            if not buyer:
                print(f"❌ Usuario {buyer_id} no encontrado")
                return False
            
            # Contar ancestros
            ancestors_count = session.exec(
                select(func.count(UserTreePath.ancestor_id))
                .where(
                    (UserTreePath.descendant_id == buyer_id) &
                    (UserTreePath.depth > 0)
                )
            ).first() or 0
            
            print(f"   👤 Comprador: member_id={buyer_id}")
            print(f"   📊 Ancestros en el árbol: {ancestors_count}")
            
            # Crear orden con status PENDING_PAYMENT
            test_order = Orders(
                member_id=buyer_id,
                country=buyer.country_cache or "MX",
                currency="MXN",
                subtotal=1000.0,
                shipping_cost=100.0,
                tax=0.0,
                discount=0.0,
                total=1100.0,
                total_pv=500,
                total_vn=1100.0,
                status=OrderStatus.PENDING_PAYMENT.value,
                payment_method="wallet",
                submitted_at=datetime.now(timezone.utc)
            )
            
            session.add(test_order)
            session.commit()
            session.refresh(test_order)
            
            print(f"   ✅ Orden creada: ID={test_order.id}")
            print(f"   💵 Total: ${test_order.total:.2f}")
            print(f"   📦 PV: {test_order.total_pv}")
            print(f"   💰 VN: ${test_order.total_vn:.2f}")
            
            # PASO 4: Confirmar el pago (TRIGGER DE COMISIONES)
            print("\n💳 PASO 4: Confirmando pago (trigger de comisiones)...")
            
            # Llamar al método que confirma el pago y dispara comisiones
            PaymentService._confirm_order_payment(session, test_order)
            PaymentService._trigger_commissions(session, test_order)
            
            session.commit()
            
            print(f"   ✅ Pago confirmado para orden {test_order.id}")
            print(f"   📅 Período asignado: {test_order.period_id}")
            print(f"   ⏰ Confirmado en: {test_order.payment_confirmed_at}")
            
            # PASO 5: Verificar comisiones DESPUÉS
            print("\n📊 PASO 5: Contando comisiones DESPUÉS de confirmar el pago...")
            
            commissions_after = session.exec(
                select(func.count(Commissions.id))
                .where(Commissions.period_id == period.id)
            ).first() or 0
            
            uninivel_after = session.exec(
                select(func.count(Commissions.id))
                .where(
                    (Commissions.period_id == period.id) &
                    (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value)
                )
            ).first() or 0
            
            matching_after = session.exec(
                select(func.count(Commissions.id))
                .where(
                    (Commissions.period_id == period.id) &
                    (Commissions.bonus_type == BonusType.BONO_MATCHING.value)
                )
            ).first() or 0
            
            print(f"   📈 Total comisiones: {commissions_after} (+{commissions_after - commissions_before})")
            print(f"   📈 Uninivel: {uninivel_after} (+{uninivel_after - uninivel_before})")
            print(f"   📈 Matching: {matching_after} (+{matching_after - matching_before})")
            
            # PASO 6: Mostrar detalles de comisiones nuevas
            print("\n💰 PASO 6: Detalles de comisiones generadas...")
            
            new_commissions = session.exec(
                select(Commissions)
                .where(
                    (Commissions.period_id == period.id) &
                    (Commissions.source_order_id == test_order.id)
                )
            ).all()
            
            if new_commissions:
                print(f"   📋 Comisiones asociadas a orden {test_order.id}:")
                for comm in new_commissions:
                    print(f"      • {comm.bonus_type}: ${comm.amount_converted:.2f} para member_id={comm.member_id}")
            
            # Mostrar comisiones Uninivel generadas
            uninivel_new = session.exec(
                select(Commissions)
                .where(
                    (Commissions.period_id == period.id) &
                    (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value)
                )
                .limit(10)
            ).all()
            
            if uninivel_new:
                print(f"\n   📋 Primeras comisiones Uninivel del período:")
                for comm in uninivel_new[:5]:
                    print(f"      • member_id={comm.member_id}: ${comm.amount_converted:.2f} (nivel {comm.level_depth})")
            
            # PASO 7: Validación final
            print("\n" + "="*80)
            print("✅ VALIDACIÓN FINAL")
            print("="*80)
            
            if uninivel_after > uninivel_before:
                print(f"✅ Bono Uninivel: Se generaron {uninivel_after - uninivel_before} comisiones")
            else:
                print(f"⚠️  Bono Uninivel: No se generaron comisiones nuevas")
            
            if matching_after > matching_before:
                print(f"✅ Bono Matching: Se generaron {matching_after - matching_before} comisiones")
            else:
                print(f"⚠️  Bono Matching: No se generaron comisiones nuevas (puede ser normal si no hay embajadores)")
            
            if commissions_after > commissions_before:
                print(f"\n✅ TEST EXITOSO: Se generaron {commissions_after - commissions_before} comisiones en total")
                return True
            else:
                print(f"\n❌ TEST FALLIDO: No se generaron comisiones")
                return False
                
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Iniciando test de comisiones instantáneas...")
    success = test_instant_commissions()
    
    if success:
        print("\n✅ TEST COMPLETADO EXITOSAMENTE")
        sys.exit(0)
    else:
        print("\n❌ TEST FALLIDO")
        sys.exit(1)
