"""
MONITOREO EN TIEMPO REAL DE LOAD TEST
======================================

Ejecutar en terminal separada DURANTE el load test.
Muestra métricas cada 5 segundos.
"""

import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import sqlmodel
from dotenv import load_dotenv
load_dotenv('.env.staging')

from NNProtect_new_website.utils.environment import Environment
DATABASE_URL = Environment.get_database_url()

def monitor_db_metrics():
    """Monitorea métricas de DB en loop."""
    engine = sqlmodel.create_engine(DATABASE_URL, echo=False)

    print("🔍 MONITOREO INICIADO - Ctrl+C para detener")
    print("="*80)

    try:
        while True:
            with sqlmodel.Session(engine) as session:
                # Connections
                result = session.exec(sqlmodel.text("""
                    SELECT
                        count(*) as total,
                        count(*) FILTER (WHERE state = 'active') as active
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """)).first()

                # Locks
                locks = session.exec(sqlmodel.text("""
                    SELECT count(*) FROM pg_locks WHERE NOT granted
                """)).first()

                # Wallet updates (proxy de actividad)
                wallet_activity = session.exec(sqlmodel.text("""
                    SELECT n_tup_upd FROM pg_stat_user_tables
                    WHERE relname = 'wallets'
                """)).first()

                print(f"[{time.strftime('%H:%M:%S')}] " +
                      f"Connections: {result[0]} ({result[1]} active) | " +
                      f"Locks: {locks[0]} | " +
                      f"Wallet Updates: {wallet_activity[0] if wallet_activity else 0}")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n✅ Monitoreo detenido")

if __name__ == "__main__":
    monitor_db_metrics()
