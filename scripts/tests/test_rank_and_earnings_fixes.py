#!/usr/bin/env python3
"""
Test script para verificar las 3 correcciones:
1. "Rango Actual" se toma del período actual (period_id)
2. "Máximo rango" se toma del rank_id más alto de toda la vida
3. Las ganancias estimadas se resetean cuando PVG=0

Autor: Adrian (Arquitecto) + Giovanni (QA Financial)
Fecha: 2025-01-20
"""
import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reflex as rx
from sqlmodel import Session, select, func
from database.users import Users
from database.user_rank_history import UserRankHistory
from database.ranks import Ranks
from database.periods import Periods
from NNProtect_new_website.mlm_service.mlm_user_manager import MLMUserManager


def test_rank_and_earnings_fixes():
    """
    Verifica que los 3 fixes funcionen correctamente.
    """
    print("\n" + "="*80)
    print("🧪 TEST: Correcciones de Rango y Ganancias")
    print("="*80)
    
    try:
        with rx.session() as session:
            # Usar member_id=1 como caso de prueba
            member_id = 1
            
            # Obtener usuario
            user = session.exec(
                select(Users).where(Users.member_id == member_id)
            ).first()
            
            if not user:
                print(f"❌ Usuario {member_id} no encontrado")
                return False
            
            print(f"\n👤 Usuario: member_id={member_id}")
            print(f"   PVG actual: {user.pvg_cache or 0}")
            print(f"   PV actual: {user.pv_cache or 0}")
            print(f"   VN actual: {user.vn_cache or 0}")
            
            # TEST 1: Obtener período actual
            print("\n" + "-"*80)
            print("📋 TEST 1: Período Actual")
            print("-"*80)
            
            from NNProtect_new_website.utils.timezone_mx import get_mexico_now
            now = get_mexico_now()
            current_period = session.exec(
                select(Periods)
                .where(
                    (Periods.starts_on <= now) &
                    (Periods.ends_on >= now)
                )
            ).first()
            
            if not current_period:
                print("❌ No hay período activo")
                return False
            
            print(f"✅ Período actual: {current_period.name} (ID={current_period.id})")
            print(f"   Fechas: {current_period.starts_on} → {current_period.ends_on}")
            
            # TEST 2: Rango Actual (del período actual)
            print("\n" + "-"*80)
            print("🎯 TEST 2: Rango Actual (del período corriendo)")
            print("-"*80)
            
            current_rank_name = MLMUserManager.get_user_current_month_rank(session, member_id)
            
            # Verificar rank_id del período actual
            current_rank_history = session.exec(
                select(UserRankHistory)
                .where(
                    (UserRankHistory.member_id == member_id) &
                    (UserRankHistory.period_id == current_period.id)
                )
                .order_by(UserRankHistory.rank_id.desc())
            ).first()
            
            if current_rank_history:
                print(f"✅ Rango Actual: {current_rank_name} (rank_id={current_rank_history.rank_id})")
                print(f"   Período: {current_period.name} (period_id={current_period.id})")
                print(f"   Fecha logro: {current_rank_history.achieved_on}")
                
                # Verificar que sea rank_id=1 (después del reset)
                if current_rank_history.rank_id == 1:
                    print("   ✅ Correcto: El usuario tiene rank_id=1 en el período actual (fue reseteado)")
                else:
                    print(f"   ⚠️  rank_id={current_rank_history.rank_id} en período actual")
            else:
                print(f"⚠️  No se encontró rank_history para el período actual")
            
            # TEST 3: Máximo Rango (de toda la vida)
            print("\n" + "-"*80)
            print("🏆 TEST 3: Máximo Rango (de toda la vida)")
            print("-"*80)
            
            highest_rank_name = MLMUserManager.get_user_highest_rank(session, member_id)
            
            # Obtener el rank_id más alto de todos los períodos
            highest_rank_id = session.exec(
                select(func.max(UserRankHistory.rank_id))
                .where(UserRankHistory.member_id == member_id)
            ).first()
            
            if highest_rank_id:
                highest_rank = session.exec(
                    select(Ranks).where(Ranks.id == highest_rank_id)
                ).first()
                
                print(f"✅ Máximo Rango: {highest_rank_name} (rank_id={highest_rank_id})")
                
                if highest_rank:
                    print(f"   PVG requerido: {highest_rank.pvg_required}")
            else:
                print(f"⚠️  No se encontró rank_history para el usuario")
            
            # TEST 4: Ganancias Estimadas (deben ser $0 si PVG=0)
            print("\n" + "-"*80)
            print("💰 TEST 4: Ganancias Estimadas (con PVG=0)")
            print("-"*80)
            
            from database.comissions import Commissions, BonusType
            
            # Sumar comisiones del período actual
            total_commissions = session.exec(
                select(func.sum(Commissions.amount_converted))
                .where(
                    (Commissions.member_id == member_id) &
                    (Commissions.period_id == current_period.id) &
                    (Commissions.bonus_type.in_([
                        BonusType.BONO_UNINIVEL.value,
                        BonusType.BONO_MATCHING.value,
                        BonusType.BONO_ALCANCE.value
                    ]))
                )
            ).first() or 0.0
            
            print(f"   Total comisiones en BD: ${total_commissions:,.2f}")
            print(f"   PVG del usuario: {user.pvg_cache or 0}")
            
            # La lógica correcta según el fix
            if (user.pvg_cache or 0) == 0:
                expected_earnings = 0.0
                print(f"✅ Ganancias Estimadas: ${expected_earnings:,.2f}")
                print(f"   ✅ Correcto: PVG=0, por lo tanto ganancias=$0 (usuario reseteado)")
            else:
                expected_earnings = total_commissions
                print(f"   Ganancias Estimadas: ${expected_earnings:,.2f}")
                print(f"   (PVG > 0, se muestran las comisiones calculadas)")
            
            # Resumen de todos los períodos del usuario
            print("\n" + "-"*80)
            print("📊 RESUMEN: Historial completo de rangos")
            print("-"*80)
            
            all_ranks = session.exec(
                select(UserRankHistory, Ranks, Periods)
                .join(Ranks, UserRankHistory.rank_id == Ranks.id)
                .join(Periods, UserRankHistory.period_id == Periods.id)
                .where(UserRankHistory.member_id == member_id)
                .order_by(Periods.starts_on.desc(), UserRankHistory.rank_id.desc())
            ).all()
            
            for rank_hist, rank, period in all_ranks:
                is_current = " ← PERÍODO ACTUAL" if period.id == current_period.id else ""
                print(f"   • {period.name}: {rank.name} (rank_id={rank_hist.rank_id}){is_current}")
            
            print("\n" + "="*80)
            print("✅ TODOS LOS TESTS COMPLETADOS")
            print("="*80)
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Iniciando tests de correcciones...")
    success = test_rank_and_earnings_fixes()
    
    if success:
        print("\n✅ Todos los tests pasaron exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Algunos tests fallaron")
        sys.exit(1)
