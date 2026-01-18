"""
Script para analizar específicamente la situación del usuario member_id=1
"""
import os
os.chdir('/Users/bradrez/Documents/NNProtect_new_website')

import reflex as rx
import sqlmodel
from database.users import Users
from database.ranks import Ranks
from database.comissions import Commissions, BonusType
from database.user_rank_history import UserRankHistory
from database.periods import Periods
from NNProtect_new_website.mlm_service.exchange_service import ExchangeService

print("="*70)
print("ANÁLISIS DETALLADO: Usuario member_id=1")
print("="*70)

with rx.session() as session:
    # 1. Obtener usuario
    user = session.exec(
        sqlmodel.select(Users).where(Users.member_id == 1)
    ).first()
    
    if not user:
        print("❌ Usuario no encontrado")
        exit()
    
    print(f"\n👤 Usuario: {user.first_name} {user.last_name}")
    print(f"   Email: {user.email}")
    print(f"   Member ID: {user.member_id}")
    print(f"   PV: {user.pv_cache}, PVG: {user.pvg_cache}")
    print(f"   País: {user.country_cache}")
    
    # 2. Historial de rangos
    rank_history = session.exec(
        sqlmodel.select(UserRankHistory)
        .where(UserRankHistory.member_id == user.member_id)
        .order_by(UserRankHistory.achieved_on)
    ).all()
    
    print(f"\n🏆 Historial de Rangos ({len(rank_history)} cambios):")
    for i, rh in enumerate(rank_history, 1):
        rank = session.exec(
            sqlmodel.select(Ranks).where(Ranks.id == rh.rank_id)
        ).first()
        
        period = None
        if rh.period_id:
            period = session.exec(
                sqlmodel.select(Periods).where(Periods.id == rh.period_id)
            ).first()
        
        period_name = period.name if period else "Sin período"
        print(f"   {i}. {rank.name if rank else 'Desconocido'} (ID={rh.rank_id})")
        print(f"      Fecha: {rh.achieved_on}")
        print(f"      Período: {period_name}")
    
    # 3. Bonos de alcance
    bonos = session.exec(
        sqlmodel.select(Commissions)
        .where(
            (Commissions.member_id == user.member_id) &
            (Commissions.bonus_type == BonusType.BONO_ALCANCE.value)
        )
        .order_by(Commissions.calculated_at)
    ).all()
    
    print(f"\n💰 Bonos de Alcance Registrados ({len(bonos)}):")
    total_bonos = 0
    for bono in bonos:
        print(f"   - ${bono.amount_converted:,.2f} {bono.currency_destination}")
        print(f"     {bono.notes}")
        print(f"     Calculado: {bono.calculated_at}")
        total_bonos += bono.amount_converted
    
    print(f"\n   TOTAL BONOS DE ALCANCE: ${total_bonos:,.2f}")
    
    # 4. Todas las comisiones del período actual
    from NNProtect_new_website.utils.timezone_mx import get_mexico_now
    now = get_mexico_now()
    current_period = session.exec(
        sqlmodel.select(Periods)
        .where(
            (Periods.starts_on <= now) &
            (Periods.ends_on >= now)
        )
    ).first()
    
    if current_period:
        print(f"\n📅 Período Actual: {current_period.name}")
        
        # Resumen por tipo de bono
        for bonus_type in [BonusType.BONO_ALCANCE, BonusType.BONO_UNINIVEL, BonusType.BONO_MATCHING]:
            total = session.exec(
                sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                .where(
                    (Commissions.member_id == user.member_id) &
                    (Commissions.period_id == current_period.id) &
                    (Commissions.bonus_type == bonus_type.value)
                )
            ).first() or 0.0
            
            count = session.exec(
                sqlmodel.select(sqlmodel.func.count(Commissions.id))  # type: ignore
                .where(
                    (Commissions.member_id == user.member_id) &
                    (Commissions.period_id == current_period.id) &
                    (Commissions.bonus_type == bonus_type.value)
                )
            ).first() or 0
            
            print(f"   {bonus_type.value}: ${total:,.2f} ({count} comisiones)")
        
        # Total del período
        grand_total = session.exec(
            sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
            .where(
                (Commissions.member_id == user.member_id) &
                (Commissions.period_id == current_period.id)
            )
        ).first() or 0.0
        
        print(f"\n   TOTAL PERÍODO: ${grand_total:,.2f}")
    
    # 5. Análisis de rangos intermedios
    print(f"\n🔍 Análisis de Rangos Intermedios:")
    
    if len(rank_history) >= 2:
        for i in range(len(rank_history) - 1):
            prev = rank_history[i]
            next = rank_history[i + 1]
            
            prev_rank = session.exec(
                sqlmodel.select(Ranks).where(Ranks.id == prev.rank_id)
            ).first()
            
            next_rank = session.exec(
                sqlmodel.select(Ranks).where(Ranks.id == next.rank_id)
            ).first()
            
            print(f"\n   Transición {i+1}: {prev_rank.name if prev_rank else '?'} → {next_rank.name if next_rank else '?'}")
            
            if next.rank_id - prev.rank_id > 1:
                print(f"   ⚠️  SALTO DE RANGOS DETECTADO")
                
                # Listar rangos intermedios
                intermediate_ranks = session.exec(
                    sqlmodel.select(Ranks)
                    .where(
                        (Ranks.id > prev.rank_id) &
                        (Ranks.id < next.rank_id)
                    )
                    .order_by(Ranks.id)
                ).all()
                
                if intermediate_ranks:
                    print(f"   Rangos intermedios omitidos:")
                    for rank in intermediate_ranks:
                        # Verificar si tiene bono
                        has_bonus = session.exec(
                            sqlmodel.select(Commissions)
                            .where(
                                (Commissions.member_id == user.member_id) &
                                (Commissions.bonus_type == BonusType.BONO_ALCANCE.value) &
                                (Commissions.notes.contains(rank.name))  # type: ignore
                            )
                        ).first()
                        
                        status = "✅ COBRADO" if has_bonus else "❌ NO COBRADO"
                        print(f"      - {rank.name}: {status}")
            else:
                print(f"   ✅ Avance consecutivo")

print(f"\n" + "="*70)
print("ANÁLISIS COMPLETADO")
print("="*70)
