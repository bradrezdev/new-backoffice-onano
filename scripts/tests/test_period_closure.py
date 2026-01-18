"""
Test manual: Simular cierre de período y pago de comisiones
"""

def test_period_closure():
    import reflex as rx
    import sqlmodel
    from datetime import datetime, timezone
    from database.periods import Periods
    from database.comissions import Commissions, CommissionStatus
    from database.wallet import Wallets
    from NNProtect_new_website.mlm_service.wallet_service import WalletService
    
    print("\n" + "="*70)
    print("🧪 TEST: Cierre de Período y Pago de Comisiones")
    print("="*70)
    
    with rx.session() as session:
        # 1. Obtener período actual
        current_period = session.exec(
            sqlmodel.select(Periods)
            .where(Periods.closed_at == None)
        ).first()
        
        if not current_period:
            print("❌ No hay período activo")
            return
        
        print(f"\n📅 Período actual: {current_period.name} (ID={current_period.id})")
        
        # 2. Obtener comisiones PENDING del período
        pending_commissions = session.exec(
            sqlmodel.select(Commissions)
            .where(
                (Commissions.period_id == current_period.id) &
                (Commissions.status == CommissionStatus.PENDING.value)
            )
        ).all()
        
        print(f"💰 Comisiones PENDING encontradas: {len(pending_commissions)}")
        
        # 3. Wallet balance ANTES (member_id=1)
        wallet_before = session.exec(
            sqlmodel.select(Wallets).where(Wallets.member_id == 1)
        ).first()
        
        balance_before = wallet_before.balance if wallet_before else 0.0
        print(f"\n💵 Wallet Balance ANTES (member_id=1): ${balance_before:.2f}")
        
        # 4. Depositar cada comisión
        deposited = 0
        failed = 0
        total_deposited = 0.0
        
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
                total_deposited += commission.amount_converted
            else:
                failed += 1
        
        session.commit()
        
        # 5. Wallet balance DESPUÉS (member_id=1)
        session.refresh(wallet_before)
        balance_after = wallet_before.balance if wallet_before else 0.0
        
        print(f"\n💵 Wallet Balance DESPUÉS (member_id=1): ${balance_after:.2f}")
        print(f"💸 Diferencia: ${balance_after - balance_before:.2f}")
        
        # 6. Verificar comisiones PAID
        paid_commissions = session.exec(
            sqlmodel.select(sqlmodel.func.count(Commissions.id))
            .where(
                (Commissions.period_id == current_period.id) &
                (Commissions.status == CommissionStatus.PAID.value)
            )
        ).first()
        
        print(f"\n📊 RESUMEN:")
        print(f"   ✅ Depositadas: {deposited}")
        print(f"   ❌ Fallidas: {failed}")
        print(f"   💰 Total depositado: ${total_deposited:.2f}")
        print(f"   ✅ Comisiones PAID: {paid_commissions}")
        
        # 7. Cerrar período
        current_period.closed_at = datetime.now(timezone.utc)
        session.add(current_period)
        session.commit()
        
        print(f"\n🔒 Período {current_period.name} cerrado exitosamente")
        print("="*70 + "\n")

if __name__ == "__main__":
    test_period_closure()
