"""
Script para verificar el historial de rangos del usuario member_id=1
"""
import os
os.chdir('/Users/bradrez/Documents/NNProtect_new_website')

import sqlmodel
from sqlmodel import Session, create_engine
from database.users import Users
from database.ranks import Ranks
from database.comissions import Commissions, BonusType
from database.user_rank_history import UserRankHistory

# Crear engine directamente
DATABASE_URL = "postgresql://postgres.hdqxuagfshuhaeefvkuh:Frida+2019@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
engine = create_engine(DATABASE_URL)

print("="*70)
print("VERIFICACIÓN: Historial de Rangos en user_rank_history")
print("="*70)

with Session(engine) as session:
    # 1. Obtener usuario
    user = session.exec(
        sqlmodel.select(Users).where(Users.member_id == 1)
    ).first()
    
    if not user:
        print("❌ Usuario no encontrado")
        exit()
    
    print(f"\n👤 Usuario: {user.first_name} {user.last_name} (member_id={user.member_id})")
    
    # 2. Obtener TODOS los registros de user_rank_history
    rank_history = session.exec(
        sqlmodel.select(UserRankHistory)
        .where(UserRankHistory.member_id == user.member_id)
        .order_by(UserRankHistory.achieved_on)
    ).all()
    
    print(f"\n🏆 Historial de Rangos en user_rank_history ({len(rank_history)} registros):")
    
    for i, rh in enumerate(rank_history, 1):
        rank = session.exec(
            sqlmodel.select(Ranks).where(Ranks.id == rh.rank_id)
        ).first()
        
        print(f"   {i}. Rango: {rank.name if rank else 'Desconocido'} (ID={rh.rank_id})")
        print(f"      Fecha: {rh.achieved_on}")
        print(f"      Period ID: {rh.period_id}")
    
    # 3. Obtener bonos de alcance YA PAGADOS
    bonos_pagados = session.exec(
        sqlmodel.select(Commissions)
        .where(
            (Commissions.member_id == user.member_id) &
            (Commissions.bonus_type == BonusType.BONO_ALCANCE.value)
        )
        .order_by(Commissions.calculated_at)
    ).all()
    
    print(f"\n💰 Bonos de Alcance PAGADOS ({len(bonos_pagados)}):")
    total_pagado = 0
    for bono in bonos_pagados:
        print(f"   - ${bono.amount_converted:,.2f} {bono.currency_destination}")
        print(f"     {bono.notes}")
        total_pagado += bono.amount_converted
    
    print(f"\n   TOTAL PAGADO: ${total_pagado:,.2f}")
    
    # 4. Identificar rangos SIN PAGAR
    print(f"\n🔍 Análisis de Rangos vs Bonos:")
    
    rangos_en_historial = set()
    for rh in rank_history:
        rank = session.exec(
            sqlmodel.select(Ranks).where(Ranks.id == rh.rank_id)
        ).first()
        if rank:
            rangos_en_historial.add(rank.name)
    
    print(f"   Rangos alcanzados: {', '.join(sorted(rangos_en_historial))}")
    
    # Verificar cuáles tienen bono pagado
    from NNProtect_new_website.modules.finance.backend.exchange_service import ExchangeService
    
    print(f"\n   Estado de bonos por rango:")
    bonos_esperados_total = 0
    
    for rango_nombre in sorted(rangos_en_historial):
        # Verificar si tiene bono pagado
        bono_existe = any(rango_nombre in bono.notes for bono in bonos_pagados)
        
        # Obtener monto esperado (hardcoded desde plan_compensacion.py)
        RANK_ADVANCEMENT_AMOUNTS = {
            "Emprendedor": {"MXN": 1500, "USD": 85, "COP": 330000},
            "Creativo": {"MXN": 3000, "USD": 165, "COP": 660000},
            "Innovador": {"MXN": 5000, "USD": 280, "COP": 1100000},
            "Embajador Transformador": {"MXN": 7500, "USD": 390, "COP": 1650000},
            "Embajador Inspirador": {"MXN": 10000, "USD": 555, "COP": 2220000},
            "Embajador Consciente": {"MXN": 20000, "USD": 1111, "COP": 4400000},
            "Embajador Solidario": {"MXN": 40000, "USD": 2222, "COP": 8800000}
        }
        bonus_amounts = RANK_ADVANCEMENT_AMOUNTS.get(rango_nombre, {})
        user_currency = ExchangeService.get_country_currency(user.country_cache or "MX")
        monto_esperado = bonus_amounts.get(user_currency, 0)
        
        if monto_esperado > 0:
            bonos_esperados_total += monto_esperado
            status = "✅ PAGADO" if bono_existe else "❌ FALTA PAGAR"
            print(f"   - {rango_nombre}: ${monto_esperado:,.2f} {user_currency} - {status}")
        else:
            print(f"   - {rango_nombre}: Sin bono definido")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Rangos alcanzados: {len(rangos_en_historial)}")
    print(f"   Bonos pagados: {len(bonos_pagados)} = ${total_pagado:,.2f}")
    print(f"   Bonos esperados: ${bonos_esperados_total:,.2f}")
    print(f"   Diferencia: ${bonos_esperados_total - total_pagado:,.2f}")

print(f"\n" + "="*70)
print("VERIFICACIÓN COMPLETADA")
print("="*70)
