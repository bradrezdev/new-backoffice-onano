"""
Script para crear nuevo período y ejecutar todos los reinicios
"""

def create_new_period_and_reset():
    import reflex as rx
    import sqlmodel
    from datetime import datetime, timezone
    from database.periods import Periods
    from database.comissions import Commissions, BonusType, CommissionStatus
    from database.users import Users, UserStatus
    from database.user_rank_history import UserRankHistory
    from NNProtect_new_website.mlm_service.period_reset_service import PeriodResetService
    
    print("\n" + "="*70)
    print("🚀 CREAR NUEVO PERÍODO Y RESETEAR SISTEMA")
    print("="*70)
    
    with rx.session() as session:
        # 1. Crear período 2025-11
        print("\n✨ PASO 1: Creando nuevo período...")
        
        new_period = Periods(
            name='2025-11',
            description='Período Noviembre 2025',
            starts_on=datetime(2025, 11, 1, tzinfo=timezone.utc),
            ends_on=datetime(2025, 11, 30, 23, 59, 59, tzinfo=timezone.utc),
            closed_at=None
        )
        
        session.add(new_period)
        session.flush()
        
        print(f"   ✅ Período creado: {new_period.name} (ID={new_period.id})")
        
        # 2. Resetear TODOS los usuarios
        print("\n🔄 PASO 2: Reseteando usuarios...")
        
        if new_period.id:
            users_reset = PeriodResetService.reset_all_users_for_new_period(
                session, new_period.id
            )
        
        session.commit()
        
        # 3. Verificar resultados
        print("\n📊 VERIFICACIÓN:")
        
        # Contar usuarios
        total_users = session.exec(
            sqlmodel.select(sqlmodel.func.count(Users.id))
        ).first()
        
        print(f"   Total usuarios: {total_users}")
        
        # Verificar usuario member_id=1
        user = session.exec(
            sqlmodel.select(Users).where(Users.member_id == 1)
        ).first()
        
        if user:
            print(f"\n   Usuario member_id=1:")
            print(f"      Status: {user.status}")
            print(f"      PV: {user.pv_cache}")
            print(f"      PVG: {user.pvg_cache}")
            print(f"      VN: {user.vn_cache}")
        
        # Verificar rank_history
        rank_history = session.exec(
            sqlmodel.select(UserRankHistory)
            .where(
                (UserRankHistory.member_id == 1) &
                (UserRankHistory.period_id == new_period.id)
            )
        ).first()
        
        if rank_history:
            print(f"\n   Rank History nuevo:")
            print(f"      member_id: {rank_history.member_id}")
            print(f"      rank_id: {rank_history.rank_id}")
            print(f"      period_id: {rank_history.period_id}")
        
        # Contar rank_history del nuevo período
        total_rank_history = session.exec(
            sqlmodel.select(sqlmodel.func.count(UserRankHistory.id))
            .where(UserRankHistory.period_id == new_period.id)
        ).first()
        
        print(f"\n   Total rank_history en período {new_period.name}: {total_rank_history}")
        
        # 4. Crear algunas comisiones PENDING de prueba
        print("\n💰 PASO 3: Creando comisiones PENDING de prueba...")
        
        test_commissions = [
            Commissions(
                member_id=1,
                bonus_type=BonusType.BONO_ALCANCE.value,
                period_id=new_period.id,
                amount_vn=100.0,
                currency_origin='MXN',
                amount_converted=1000.0,
                currency_destination='MXN',
                exchange_rate=1.0,
                status=CommissionStatus.PENDING.value,
                notes='Test comisión 1'
            ),
            Commissions(
                member_id=1,
                bonus_type=BonusType.BONO_UNINIVEL.value,
                period_id=new_period.id,
                amount_vn=50.0,
                currency_origin='MXN',
                amount_converted=500.0,
                currency_destination='MXN',
                exchange_rate=1.0,
                status=CommissionStatus.PENDING.value,
                notes='Test comisión 2'
            ),
            Commissions(
                member_id=2,
                bonus_type=BonusType.BONO_UNINIVEL.value,
                period_id=new_period.id,
                amount_vn=30.0,
                currency_origin='MXN',
                amount_converted=300.0,
                currency_destination='MXN',
                exchange_rate=1.0,
                status=CommissionStatus.PENDING.value,
                notes='Test comisión 3'
            ),
        ]
        
        for comm in test_commissions:
            session.add(comm)
        
        session.commit()
        
        print(f"   ✅ {len(test_commissions)} comisiones PENDING creadas")
        print(f"   💰 Total: $1,800.00")
        
        print("\n" + "="*70)
        print("✅ PROCESO COMPLETADO")
        print("="*70)
        print(f"\nPuedes probar el cierre de período con el botón del Admin Panel")
        print(f"o ejecutar: python3 test_simplified_closure.py\n")

if __name__ == "__main__":
    create_new_period_and_reset()
