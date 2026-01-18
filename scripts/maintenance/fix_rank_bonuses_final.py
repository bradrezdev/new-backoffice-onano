"""
Script de CORRECCIÓN RETROACTIVA de Bonos de Alcance Faltantes.

Este script revisa TODOS los registros en user_rank_history y paga los bonos
de alcance que faltan, respetando la regla de "1 vez en la vida por rango".

Ejecutar DENTRO del contexto de Reflex para tener acceso a rx.session()
"""

def fix_missing_rank_bonuses():
    import reflex as rx
    import sqlmodel
    from database.users import Users
    from database.ranks import Ranks
    from database.comissions import Commissions, BonusType
    from database.user_rank_history import UserRankHistory
    from NNProtect_new_website.mlm_service.exchange_service import ExchangeService
    from datetime import datetime, timezone
    
    # Montos de bonos por rango
    RANK_ADVANCEMENT_AMOUNTS = {
        "Emprendedor": {"MXN": 1500, "USD": 85, "COP": 330000},
        "Creativo": {"MXN": 3000, "USD": 165, "COP": 660000},
        "Innovador": {"MXN": 5000, "USD": 280, "COP": 1100000},
        "Embajador Transformador": {"MXN": 7500, "USD": 390, "COP": 1650000},
        "Embajador Inspirador": {"MXN": 10000, "USD": 555, "COP": 2220000},
        "Embajador Consciente": {"MXN": 20000, "USD": 1111, "COP": 4400000},
        "Embajador Solidario": {"MXN": 40000, "USD": 2222, "COP": 8800000}
    }
    
    print("="*70)
    print("CORRECCIÓN RETROACTIVA: Bonos de Alcance Faltantes")
    print("="*70)
    
    with rx.session() as session:
        # Obtener TODOS los registros de user_rank_history
        all_rank_history = session.exec(
            sqlmodel.select(UserRankHistory)
            .order_by(UserRankHistory.member_id, UserRankHistory.achieved_on)
        ).all()
        
        print(f"\n📊 Procesando {len(all_rank_history)} registros de rank_history...")
        
        corrections = []
        
        for rh in all_rank_history:
            # Obtener usuario
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == rh.member_id)
            ).first()
            
            if not user:
                continue
            
            # Obtener rango
            rank = session.exec(
                sqlmodel.select(Ranks).where(Ranks.id == rh.rank_id)
            ).first()
            
            if not rank or rank.name not in RANK_ADVANCEMENT_AMOUNTS:
                continue  # Sin bono definido
            
            # Verificar si YA tiene bono pagado para este rango
            existing_bonus = session.exec(
                sqlmodel.select(Commissions)
                .where(
                    (Commissions.member_id == rh.member_id) &
                    (Commissions.bonus_type == BonusType.BONO_ALCANCE.value) &
                    (Commissions.notes.contains(rank.name))  # type: ignore
                )
            ).first()
            
            if existing_bonus:
                continue  # Ya tiene bono pagado
            
            # FALTA PAGAR: Obtener monto según país
            user_currency = ExchangeService.get_country_currency(user.country_cache or "MX")
            bonus_amounts = RANK_ADVANCEMENT_AMOUNTS[rank.name]
            amount = bonus_amounts.get(user_currency, 0)
            
            if amount <= 0:
                continue
            
            corrections.append({
                "member_id": rh.member_id,
                "user_name": f"{user.first_name} {user.last_name}",
                "rank_name": rank.name,
                "amount": amount,
                "currency": user_currency,
                "period_id": rh.period_id,
                "achieved_on": rh.achieved_on
            })
        
        if not corrections:
            print("\n✅ No hay bonos faltantes por pagar")
            return
        
        print(f"\n💰 BONOS FALTANTES ENCONTRADOS: {len(corrections)}")
        
        total_to_pay = {}
        for corr in corrections:
            currency = corr["currency"]
            total_to_pay[currency] = total_to_pay.get(currency, 0) + corr["amount"]
            
            print(f"\n   {corr['user_name']} (member_id={corr['member_id']})")
            print(f"   Rango: {corr['rank_name']}")
            print(f"   Monto: ${corr['amount']:,.2f} {corr['currency']}")
            print(f"   Alcanzado: {corr['achieved_on']}")
        
        print(f"\n📊 TOTAL A PAGAR:")
        for currency, total in total_to_pay.items():
            print(f"   {currency}: ${total:,.2f}")
        
        # Confirmar
        print(f"\n" + "="*70)
        response = input("¿Confirmar y aplicar corrección? (s/n): ")
        
        if response.lower() != 's':
            print("\n❌ Corrección cancelada")
            return
        
        # Aplicar correcciones
        for corr in corrections:
            commission = Commissions(
                member_id=corr["member_id"],
                bonus_type=BonusType.BONO_ALCANCE.value,
                source_member_id=None,
                source_order_id=None,
                period_id=corr["period_id"],
                level_depth=None,
                amount_vn=corr["amount"],
                currency_origin=corr["currency"],
                amount_converted=corr["amount"],
                currency_destination=corr["currency"],
                exchange_rate=1.0,
                calculated_at=datetime.now(timezone.utc),
                paid_at=None,
                notes=f"Bono por Alcance - Rango: {corr['rank_name']} (CORRECCIÓN RETROACTIVA)"
            )
            
            session.add(commission)
        
        session.commit()
        
        print(f"\n✅ CORRECCIÓN APLICADA: {len(corrections)} bonos pagados")
        print("="*70)

# Ejecutar función
if __name__ == "__main__":
    fix_missing_rank_bonuses()
