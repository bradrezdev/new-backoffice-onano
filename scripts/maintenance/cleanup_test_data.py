"""
Script para limpiar datos de prueba antes de ejecutar tests E2E.
Elimina usuarios con member_id en rango de testing (90000-90999).
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import reflex as rx
import sqlmodel
from database.users import Users
from database.wallet import Wallets, WalletTransactions
from database.orders import Orders
from database.order_items import OrderItems
from database.comissions import Commissions
from database.usertreepaths import UserTreePath
from database.user_rank_history import UserRankHistory

from NNProtect_new_website.utils.environment import Environment
DATABASE_URL = Environment.get_database_url()

def cleanup_test_data():
    """Elimina todos los datos de prueba de member_id 90000-90999."""
    engine = sqlmodel.create_engine(DATABASE_URL, echo=False)

    with sqlmodel.Session(engine) as session:
        try:
            print("Limpiando datos de prueba...")

            # 1. Eliminar comisiones
            commissions = session.exec(
                sqlmodel.select(Commissions).where(
                    Commissions.member_id >= 90000
                )
            ).all()
            for comm in commissions:
                session.delete(comm)
            print(f"✓ Eliminadas {len(commissions)} comisiones")

            # 2. Eliminar transacciones de wallet PRIMERO (tienen FK a orders)
            wallet_txs = session.exec(
                sqlmodel.select(WalletTransactions).where(
                    WalletTransactions.member_id >= 90000
                )
            ).all()
            for tx in wallet_txs:
                session.delete(tx)
            print(f"✓ Eliminadas {len(wallet_txs)} transacciones de wallet")

            # 3. Eliminar items de orden
            order_items = session.exec(
                sqlmodel.select(OrderItems).join(Orders).where(
                    Orders.member_id >= 90000
                )
            ).all()
            for item in order_items:
                session.delete(item)
            print(f"✓ Eliminados {len(order_items)} order items")

            # 4. Eliminar órdenes
            orders = session.exec(
                sqlmodel.select(Orders).where(Orders.member_id >= 90000)
            ).all()
            for order in orders:
                session.delete(order)
            print(f"✓ Eliminadas {len(orders)} órdenes")

            # 6. Eliminar wallets
            wallets = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id >= 90000)
            ).all()
            for wallet in wallets:
                session.delete(wallet)
            print(f"✓ Eliminadas {len(wallets)} wallets")

            # 7. Eliminar rank history
            rank_history = session.exec(
                sqlmodel.select(UserRankHistory).where(
                    UserRankHistory.member_id >= 90000
                )
            ).all()
            for history in rank_history:
                session.delete(history)
            print(f"✓ Eliminados {len(rank_history)} rank history records")

            # 8. Eliminar paths genealógicos
            tree_paths = session.exec(
                sqlmodel.select(UserTreePath).where(
                    (UserTreePath.descendant_id >= 90000) |
                    (UserTreePath.ancestor_id >= 90000)
                )
            ).all()
            for path in tree_paths:
                session.delete(path)
            print(f"✓ Eliminados {len(tree_paths)} tree paths")

            # 9. Eliminar usuarios
            users = session.exec(
                sqlmodel.select(Users).where(Users.member_id >= 90000)
            ).all()
            for user in users:
                session.delete(user)
            print(f"✓ Eliminados {len(users)} usuarios")

            session.commit()
            print("\n✅ Limpieza completada exitosamente")
            return True

        except Exception as e:
            print(f"\n❌ Error durante limpieza: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return False

if __name__ == "__main__":
    success = cleanup_test_data()
    sys.exit(0 if success else 1)
