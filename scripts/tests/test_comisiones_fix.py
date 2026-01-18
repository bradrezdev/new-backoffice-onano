"""
Script de prueba para verificar el fix de comisiones:
1. PVG se resetea correctamente
2. vn_cache se resetea correctamente  
3. Comisiones se depositan en billeteras
4. Comisiones se guardan en tabla 'commissions'
"""

import sqlmodel
from database import engine
from database.users import Users
from database.comissions import Commissions, CommissionStatus
from database.wallet import Wallets, WalletTransactions
from database.periods import Periods

def test_estado_actual():
    """Verifica el estado actual antes del cierre de período"""
    
    with sqlmodel.Session(engine) as session:
        print("="*80)
        print("📊 ESTADO ACTUAL DE LA BASE DE DATOS")
        print("="*80)
        
        # 1. Verificar usuarios y sus volúmenes
        print("\n1️⃣ USUARIOS Y VOLÚMENES:")
        users = session.exec(sqlmodel.select(Users)).all()
        for user in users:
            print(f"   User {user.member_id}: pv_cache={user.pv_cache}, pvg_cache={user.pvg_cache}, vn_cache={user.vn_cache}")
        
        # 2. Verificar comisiones PENDING
        print("\n2️⃣ COMISIONES PENDING:")
        pending = session.exec(
            sqlmodel.select(Commissions)
            .where(Commissions.status == CommissionStatus.PENDING.value)
        ).all()
        print(f"   Total comisiones PENDING: {len(pending)}")
        for comm in pending:
            print(f"   - User {comm.member_id}: {comm.bonus_type} = ${comm.amount_converted:.2f} {comm.currency_destination}")
        
        # 3. Verificar billeteras
        print("\n3️⃣ BILLETERAS:")
        wallets = session.exec(sqlmodel.select(Wallets)).all()
        for wallet in wallets:
            print(f"   User {wallet.member_id}: Balance = ${wallet.balance:.2f} {wallet.currency}")
        
        # 4. Verificar transacciones de wallet
        print("\n4️⃣ TRANSACCIONES DE WALLET:")
        transactions = session.exec(sqlmodel.select(WalletTransactions)).all()
        print(f"   Total transacciones: {len(transactions)}")
        for tx in transactions:
            print(f"   - User {tx.member_id}: {tx.transaction_type} = ${tx.amount:.2f} {tx.currency}")
        
        # 5. Verificar período actual
        print("\n5️⃣ PERÍODO ACTUAL:")
        period = session.exec(
            sqlmodel.select(Periods)
            .where(Periods.status == "ACTIVE")
        ).first()
        if period:
            print(f"   Período {period.id}: {period.name} ({period.status})")
        else:
            print("   ⚠️  No hay período ACTIVE")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    test_estado_actual()
