"""
SEED DATA PARA LOAD TESTING
============================

Genera datos sintéticos controlados:
- 200 usuarios de prueba (ID 80000-80199)
- 200 wallets con balance controlado
- Productos de catálogo (reutiliza existentes)
- Estructura MLM básica para comisiones

IMPORTANTE: Usa member_ids en rango 80000+ para evitar conflictos con producción
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import sqlmodel
from datetime import datetime, timezone
from database.users import Users, UserStatus
from database.wallet import Wallets, WalletStatus
from database.periods import Periods
from NNProtect_new_website.utils.environment import Environment

# Cargar .env.staging
from dotenv import load_dotenv
load_dotenv('.env.staging')

DATABASE_URL = Environment.get_database_url()

def seed_load_test_data():
    """Genera 200 usuarios con wallets para load testing."""
    engine = sqlmodel.create_engine(DATABASE_URL, echo=True)

    with sqlmodel.Session(engine) as session:
        print("🌱 Iniciando seeding de datos para load testing...")

        # 1. Crear período activo
        existing_period = session.exec(
            sqlmodel.select(Periods).where(Periods.name == "Load Test Period")
        ).first()

        if not existing_period:
            period = Periods(
                name="Load Test Period",
                description="Período para pruebas de carga",
                starts_on=datetime.utcnow(),
                ends_on=datetime(2025, 12, 31, 23, 59, 59),
                closed_at=None
            )
            session.add(period)
            session.flush()
            print("✅ Período de prueba creado")
        else:
            print("✅ Período de prueba ya existe")

        # 2. Crear 200 usuarios de prueba
        users_created = 0
        wallets_created = 0

        for i in range(200):
            member_id = 80000 + i

            # Verificar si ya existe
            existing = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()

            if existing:
                print(f"⏭️  Usuario {member_id} ya existe, saltando...")
                continue

            user = Users(
                member_id=member_id,
                first_name=f"LoadTest",
                last_name=f"User{i:03d}",
                email_cache=f"loadtest{i}@example.com",
                country_cache="MX",
                status=UserStatus.QUALIFIED,
                sponsor_id=80000 if i > 0 else None,  # Todos patrocinados por user 80000
                pv_cache=0,
                pvg_cache=0
            )
            session.add(user)

            # Crear wallet con balance aleatorio entre 5000-10000 MXN
            import random
            balance = random.uniform(5000, 10000)

            wallet = Wallets(
                member_id=member_id,
                balance=balance,
                currency="MXN",
                status=WalletStatus.ACTIVE.value
            )
            session.add(wallet)

            users_created += 1
            wallets_created += 1

            if users_created % 50 == 0:
                session.flush()
                print(f"✅ Creados {users_created} usuarios...")

        session.commit()
        print(f"\n{'='*80}")
        print(f"✅ SEED COMPLETADO:")
        print(f"   - Usuarios creados: {users_created}")
        print(f"   - Wallets creados: {wallets_created}")
        print(f"   - Rango de IDs: 80000-80199")
        print(f"{'='*80}\n")

if __name__ == "__main__":
    try:
        seed_load_test_data()
    except Exception as e:
        print(f"❌ Error durante seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
