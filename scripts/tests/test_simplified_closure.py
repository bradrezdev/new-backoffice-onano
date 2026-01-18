"""
Test completo: Cierre de período simplificado
Verifica:
1. Pago de comisiones PENDING → PAID
2. Creación de nuevo período
3. Reseteo de usuarios (status, pv, pvg, vn, rank_history)
"""

def test_simplified_period_closure():
    import reflex as rx
    import sqlmodel
    from datetime import datetime, timezone
    from database.periods import Periods
    from database.comissions import Commissions, CommissionStatus
    from database.wallet import Wallets
    from database.users import Users, UserStatus
    from database.user_rank_history import UserRankHistory
    from NNProtect_new_website.mlm_service.wallet_service import WalletService
    from NNProtect_new_website.mlm_service.period_reset_service import PeriodResetService
    
    print("\n" + "="*70)
    print("🧪 TEST: Cierre de Período Simplificado")
    print("="*70)
    
    with rx.session() as session:
        # === ESTADO INICIAL ===
        print("\n📊 ESTADO INICIAL:")
        
        # Período actual
        current_period = session.exec(
            sqlmodel.select(Periods)
            .where(Periods.closed_at == None)
        ).first()
        
        if not current_period or not current_period.id:
            print("❌ No hay período activo")
            return
        
        print(f"   Período: {current_period.name} (ID={current_period.id})")
        
        # Comisiones PENDING
        pending_count = session.exec(
            sqlmodel.select(sqlmodel.func.count(Commissions.id))
            .where(
                (Commissions.period_id == current_period.id) &
                (Commissions.status == CommissionStatus.PENDING.value)
            )
        ).first()
        
        print(f"   Comisiones PENDING: {pending_count}")
        
        # Wallet de member_id=1 ANTES
        wallet_before = session.exec(
            sqlmodel.select(Wallets).where(Wallets.member_id == 1)
        ).first()
        
        balance_before = wallet_before.balance if wallet_before else 0.0
        print(f"   Wallet (member_id=1): ${balance_before:.2f}")
        
        # Usuario member_id=1 ANTES
        user_before = session.exec(
            sqlmodel.select(Users).where(Users.member_id == 1)
        ).first()
        
        if user_before:
            print(f"   Usuario status: {user_before.status}")
            print(f"   Usuario PV: {user_before.pv_cache}")
            print(f"   Usuario PVG: {user_before.pvg_cache}")
            print(f"   Usuario VN: {user_before.vn_cache}")
        
        # === PASO 1: PAGAR COMISIONES PENDING ===
        print("\n💰 PASO 1: Pagando comisiones PENDING...")
        
        pending_commissions = session.exec(
            sqlmodel.select(Commissions)
            .where(
                (Commissions.period_id == current_period.id) &
                (Commissions.status == CommissionStatus.PENDING.value)
            )
        ).all()
        
        deposited = 0
        failed = 0
        total_amount = 0.0
        
        for commission in pending_commissions:
            if commission.id is None:
                failed += 1
                continue
            
            success = WalletService.deposit_commission(
                session=session,
                member_id=commission.member_id,
                commission_id=commission.id,
                amount=commission.amount_converted,
                currency=commission.currency_destination,
                description=commission.notes
            )
            
            if success:
                deposited += 1
                total_amount += commission.amount_converted
            else:
                failed += 1
        
        print(f"   ✅ Depositadas: {deposited}")
        print(f"   ❌ Fallidas: {failed}")
        print(f"   💰 Total: ${total_amount:.2f}")
        
        # === PASO 2: CERRAR PERÍODO ===
        print("\n🔒 PASO 2: Cerrando período actual...")
        
        current_period.closed_at = datetime.now(timezone.utc)
        session.add(current_period)
        
        print(f"   ✅ Período {current_period.name} cerrado")
        
        # === PASO 3: CREAR NUEVO PERÍODO ===
        print("\n✨ PASO 3: Creando nuevo período...")
        
        now = datetime.now(timezone.utc)
        
        # Obtener el último período para calcular el siguiente
        last_period = session.exec(
            sqlmodel.select(Periods)
            .order_by(Periods.id.desc())
        ).first()
        
        # Calcular siguiente mes basado en el período cerrado
        closed_year = int(current_period.name.split('-')[0])
        closed_month = int(current_period.name.split('-')[1])
        
        next_month = closed_month + 1 if closed_month < 12 else 1
        next_year = closed_year if closed_month < 12 else closed_year + 1
        
        new_period_name = f"{next_year}-{next_month:02d}"
        
        # Verificar si existe
        existing = session.exec(
            sqlmodel.select(Periods).where(Periods.name == new_period_name)
        ).first()
        
        if existing:
            print(f"   ℹ️  Período {new_period_name} ya existe (ID={existing.id})")
            new_period = existing
            users_reset = 0
        else:
            new_period = Periods(
                name=new_period_name,
                description=f"Período {new_period_name}",
                starts_on=now,
                ends_on=datetime(next_year, next_month, 28, 23, 59, 59, tzinfo=timezone.utc)
            )
            
            session.add(new_period)
            session.flush()
            
            print(f"   ✅ Nuevo período: {new_period.name} (ID={new_period.id})")
            
            # === PASO 4: RESETEAR USUARIOS ===
            print("\n🔄 PASO 4: Reseteando usuarios...")
            
            if new_period.id:
                users_reset = PeriodResetService.reset_all_users_for_new_period(
                    session, new_period.id
                )
                print(f"   ✅ {users_reset} usuarios reseteados")
        
        session.commit()
        
        # === ESTADO FINAL ===
        print("\n📊 ESTADO FINAL:")
        
        # Comisiones PAID del período cerrado
        paid_count = session.exec(
            sqlmodel.select(sqlmodel.func.count(Commissions.id))
            .where(
                (Commissions.period_id == current_period.id) &
                (Commissions.status == CommissionStatus.PAID.value)
            )
        ).first()
        
        print(f"   Comisiones PAID (período cerrado): {paid_count}")
        
        # Wallet DESPUÉS
        session.refresh(wallet_before)
        balance_after = wallet_before.balance if wallet_before else 0.0
        print(f"   Wallet (member_id=1): ${balance_after:.2f}")
        print(f"   Diferencia: +${balance_after - balance_before:.2f}")
        
        # Usuario DESPUÉS
        session.refresh(user_before)
        print(f"   Usuario status: {user_before.status}")
        print(f"   Usuario PV: {user_before.pv_cache}")
        print(f"   Usuario PVG: {user_before.pvg_cache}")
        print(f"   Usuario VN: {user_before.vn_cache}")
        
        # Verificar rank_history nuevo
        new_rank_history = session.exec(
            sqlmodel.select(UserRankHistory)
            .where(
                (UserRankHistory.member_id == 1) &
                (UserRankHistory.period_id == new_period.id)
            )
        ).first()
        
        if new_rank_history:
            print(f"   Rank History nuevo: rank_id={new_rank_history.rank_id}, period_id={new_rank_history.period_id}")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETADO")
        print("="*70 + "\n")

if __name__ == "__main__":
    test_simplified_period_closure()
