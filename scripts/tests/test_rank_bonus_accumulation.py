"""
Script para probar el sistema de bonos acumulativos por avance de rango.
"""
import os
os.chdir('/Users/bradrez/Documents/NNProtect_new_website')

import reflex as rx
import sqlmodel
from database.users import Users
from database.ranks import Ranks
from database.comissions import Commissions, BonusType
from database.periods import Periods
from NNProtect_new_website.mlm_service.rank_service import RankService
from NNProtect_new_website.utils.timezone_mx import get_mexico_now

print("="*70)
print("TEST: Sistema de Bonos Acumulativos por Avance de Rango")
print("="*70)

with rx.session() as session:
    # 1. Obtener usuario de prueba (member_id=1)
    user = session.exec(
        sqlmodel.select(Users).where(Users.member_id == 1)
    ).first()
    
    if not user:
        print("❌ Usuario no encontrado")
        exit()
    
    print(f"\n👤 Usuario: {user.first_name} {user.last_name} (member_id={user.member_id})")
    print(f"   PV: {user.pv_cache}, PVG: {user.pvg_cache}")
    
    # 2. Obtener rango actual
    current_rank_id = RankService.get_user_current_rank(session, user.member_id)
    
    if current_rank_id:
        current_rank = session.exec(
            sqlmodel.select(Ranks).where(Ranks.id == current_rank_id)
        ).first()
        print(f"   Rango actual: {current_rank.name} (ID={current_rank_id})")
    else:
        print(f"   ⚠️  Sin rango asignado")
    
    # 3. Obtener período actual
    now = get_mexico_now()
    current_period = session.exec(
        sqlmodel.select(Periods)
        .where(
            (Periods.starts_on <= now) &
            (Periods.ends_on >= now)
        )
    ).first()
    
    if not current_period:
        print("❌ No hay período activo")
        exit()
    
    print(f"\n📅 Período actual: {current_period.name} (ID={current_period.id})")
    
    # 4. Listar bonos de alcance ACTUALES
    bonos_actuales = session.exec(
        sqlmodel.select(Commissions)
        .where(
            (Commissions.member_id == user.member_id) &
            (Commissions.bonus_type == BonusType.BONO_ALCANCE.value)
        )
        .order_by(Commissions.calculated_at)
    ).all()
    
    print(f"\n💰 Bonos de Alcance Actuales:")
    total_alcance_actual = 0
    for bono in bonos_actuales:
        print(f"   - ${bono.amount_converted:,.2f} {bono.currency_destination} - {bono.notes}")
        total_alcance_actual += bono.amount_converted
    print(f"   TOTAL ACTUAL: ${total_alcance_actual:,.2f}")
    
    # 5. Simular promoción de rango
    print(f"\n" + "="*70)
    print("SIMULACIÓN: Promover a usuario manualmente")
    print("="*70)
    
    # Obtener todos los rangos disponibles
    all_ranks = session.exec(
        sqlmodel.select(Ranks).order_by(Ranks.id)
    ).all()
    
    print(f"\nRangos disponibles:")
    for rank in all_ranks:
        marker = "✅" if rank.id == current_rank_id else " "
        print(f"  {marker} {rank.id}. {rank.name} (PV req: {rank.pv_requirement}, PVG req: {rank.pvg_requirement})")
    
    # Verificar si el usuario cumple requisitos para un rango superior
    print(f"\n🔍 Verificando requisitos para rangos superiores...")
    
    eligible_rank = None
    for rank in all_ranks:
        if rank.id <= current_rank_id:
            continue  # Skip current and lower ranks
        
        # Check if user meets requirements
        meets_pv = user.pv_cache >= (rank.pv_requirement or 0)
        meets_pvg = user.pvg_cache >= (rank.pvg_requirement or 0)
        
        if meets_pv and meets_pvg:
            eligible_rank = rank
            print(f"   ✅ Cumple requisitos para: {rank.name}")
        else:
            print(f"   ❌ No cumple {rank.name}: PV={meets_pv}, PVG={meets_pvg}")
            break  # Stop at first rank not met
    
    if eligible_rank:
        print(f"\n🎯 Usuario puede ser promovido a: {eligible_rank.name}")
        print(f"\nEsto generará bonos para TODOS los rangos intermedios:")
        
        # Calcular rangos intermedios
        intermediate_ranks = session.exec(
            sqlmodel.select(Ranks)
            .where(
                (Ranks.id > current_rank_id) &
                (Ranks.id <= eligible_rank.id)
            )
            .order_by(Ranks.id)
        ).all()
        
        expected_bonus_total = 0
        for rank in intermediate_ranks:
            from NNProtect_new_website.mlm_service.commission_service import CommissionService
            bonus_amounts = CommissionService.ACHIEVEMENT_BONUS_AMOUNTS.get(rank.name, {})
            user_currency = "MXN"  # Assuming MX
            amount = bonus_amounts.get(user_currency, 0)
            expected_bonus_total += amount
            print(f"   - {rank.name}: ${amount:,.2f} {user_currency}")
        
        print(f"   TOTAL ESPERADO: ${expected_bonus_total:,.2f}")
        
        # Preguntar si quiere aplicar la promoción
        apply = input(f"\n¿Aplicar promoción a {eligible_rank.name}? (s/n): ")
        
        if apply.lower() == 's':
            print(f"\n🚀 Aplicando promoción...")
            success = RankService.promote_user_rank(session, user.member_id, eligible_rank.id)
            
            if success:
                session.commit()
                print(f"\n✅ Promoción aplicada exitosamente!")
                
                # Verificar bonos generados
                bonos_nuevos = session.exec(
                    sqlmodel.select(Commissions)
                    .where(
                        (Commissions.member_id == user.member_id) &
                        (Commissions.bonus_type == BonusType.BONO_ALCANCE.value)
                    )
                    .order_by(Commissions.calculated_at)
                ).all()
                
                print(f"\n💰 Bonos de Alcance DESPUÉS de promoción:")
                total_alcance_nuevo = 0
                for bono in bonos_nuevos:
                    print(f"   - ${bono.amount_converted:,.2f} {bono.currency_destination} - {bono.notes}")
                    total_alcance_nuevo += bono.amount_converted
                print(f"   TOTAL NUEVO: ${total_alcance_nuevo:,.2f}")
                print(f"   DIFERENCIA: +${total_alcance_nuevo - total_alcance_actual:,.2f}")
            else:
                session.rollback()
                print(f"\n❌ Error al aplicar promoción")
        else:
            print(f"\n⚠️  Promoción cancelada")
    else:
        print(f"\n⚠️  Usuario NO cumple requisitos para ningún rango superior")

print(f"\n" + "="*70)
print("TEST COMPLETADO")
print("="*70)
