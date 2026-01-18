"""
Script para CORREGIR bonos de alcance faltantes de rangos intermedios.

Este script identifica usuarios que avanzaron múltiples rangos y no cobraron
los bonos de los rangos intermedios, y los registra retroactivamente.
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
from NNProtect_new_website.mlm_service.commission_service import CommissionService
from NNProtect_new_website.mlm_service.exchange_service import ExchangeService
from datetime import datetime, timezone

print("="*70)
print("CORRECCIÓN: Bonos de Alcance Faltantes de Rangos Intermedios")
print("="*70)

with rx.session() as session:
    # 1. Obtener TODOS los usuarios
    all_users = session.exec(
        sqlmodel.select(Users)
        .where(Users.member_id.isnot(None))  # type: ignore
    ).all()
    
    print(f"\n📊 Analizando {len(all_users)} usuarios...")
    
    corrections_made = 0
    total_bonuses_added = 0
    
    for user in all_users:
        # 2. Obtener historial de rangos del usuario
        rank_history = session.exec(
            sqlmodel.select(UserRankHistory)
            .where(UserRankHistory.member_id == user.member_id)
            .order_by(UserRankHistory.achieved_on)
        ).all()
        
        if not rank_history or len(rank_history) < 2:
            continue  # Solo 1 rango o ninguno, no hay intermedios
        
        # 3. Analizar cada transición de rango
        for i in range(len(rank_history) - 1):
            prev_rank_id = rank_history[i].rank_id
            next_rank_id = rank_history[i + 1].rank_id
            
            # Verificar si hay rangos intermedios
            if next_rank_id - prev_rank_id <= 1:
                continue  # Avance consecutivo, no hay intermedios
            
            print(f"\n🔍 Usuario {user.member_id}: Salto de rango {prev_rank_id} → {next_rank_id}")
            
            # 4. Obtener rangos intermedios
            intermediate_ranks = session.exec(
                sqlmodel.select(Ranks)
                .where(
                    (Ranks.id > prev_rank_id) &
                    (Ranks.id < next_rank_id)  # Solo intermedios, no el destino
                )
                .order_by(Ranks.id)
            ).all()
            
            if not intermediate_ranks:
                continue
            
            print(f"   Rangos intermedios no cobrados:")
            
            for rank in intermediate_ranks:
                # 5. Verificar si ya existe bono para este rango
                existing_bonus = session.exec(
                    sqlmodel.select(Commissions)
                    .where(
                        (Commissions.member_id == user.member_id) &
                        (Commissions.bonus_type == BonusType.BONO_ALCANCE.value) &
                        (Commissions.notes.contains(rank.name))  # type: ignore
                    )
                ).first()
                
                if existing_bonus:
                    print(f"   ✅ {rank.name}: Ya cobrado (${existing_bonus.amount_converted})")
                    continue
                
                # 6. Obtener monto del bono según país del usuario
                user_currency = ExchangeService.get_country_currency(user.country_cache or "MX")
                bonus_amounts = CommissionService.ACHIEVEMENT_BONUS_AMOUNTS.get(rank.name, {})
                amount = bonus_amounts.get(user_currency)
                
                if not amount:
                    print(f"   ⚠️  {rank.name}: No hay monto definido para {user_currency}")
                    continue
                
                # 7. Obtener período en el que alcanzó el rango siguiente
                period_id = rank_history[i + 1].period_id
                
                # 8. Crear comisión retroactiva
                commission = Commissions(
                    member_id=user.member_id,
                    bonus_type=BonusType.BONO_ALCANCE.value,
                    source_member_id=None,
                    source_order_id=None,
                    period_id=period_id,
                    level_depth=None,
                    amount_vn=amount,
                    currency_origin=user_currency,
                    amount_converted=amount,
                    currency_destination=user_currency,
                    exchange_rate=1.0,
                    calculated_at=datetime.now(timezone.utc),
                    paid_at=None,
                    notes=f"Bono por Alcance - Rango: {rank.name} (CORRECCIÓN RETROACTIVA)"
                )
                
                session.add(commission)
                print(f"   ✨ {rank.name}: Bono agregado ${amount:,.2f} {user_currency} (NUEVO)")
                
                total_bonuses_added += 1
            
            corrections_made += 1
    
    # 9. Confirmar cambios
    if corrections_made > 0:
        print(f"\n" + "="*70)
        print(f"📈 RESUMEN:")
        print(f"   Usuarios corregidos: {corrections_made}")
        print(f"   Bonos agregados: {total_bonuses_added}")
        print("="*70)
        
        confirm = input(f"\n¿Confirmar cambios en la base de datos? (s/n): ")
        
        if confirm.lower() == 's':
            session.commit()
            print(f"\n✅ Cambios aplicados exitosamente!")
            
            # Mostrar comisiones agregadas
            print(f"\n💰 Comisiones agregadas:")
            new_commissions = session.exec(
                sqlmodel.select(Commissions)
                .where(
                    (Commissions.bonus_type == BonusType.BONO_ALCANCE.value) &
                    (Commissions.notes.contains("CORRECCIÓN RETROACTIVA"))  # type: ignore
                )
                .order_by(Commissions.member_id)
            ).all()
            
            for comm in new_commissions:
                user = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == comm.member_id)
                ).first()
                if user:
                    print(f"   - {user.first_name} {user.last_name}: ${comm.amount_converted:,.2f} {comm.currency_destination} - {comm.notes}")
        else:
            session.rollback()
            print(f"\n❌ Cambios descartados")
    else:
        print(f"\n✅ No se encontraron correcciones necesarias")

print(f"\n" + "="*70)
print("CORRECCIÓN COMPLETADA")
print("="*70)
