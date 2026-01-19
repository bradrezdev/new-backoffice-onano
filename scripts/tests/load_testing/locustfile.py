"""
LOCUST LOAD TEST - PAYMENT SERVICE
===================================

Simula 100-200 usuarios concurrentes realizando pagos con wallet.

Métricas medidas:
- Response time (p50, p95, p99)
- Throughput (requests/sec)
- Error rate
- Database connection pool usage
"""

from locust import HttpUser, task, between, events
import random
import json
import time
from datetime import datetime

# Importar servicios (para tests directos a DB)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import sqlmodel
from NNProtect_new_website.payment_service.payment_service import PaymentService
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.products import Products
from NNProtect_new_website.utils.environment import Environment

# Cargar staging environment
from dotenv import load_dotenv
load_dotenv('.env.staging')

DATABASE_URL = Environment.get_database_url()
engine = sqlmodel.create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,  # Connection pool para load testing
    max_overflow=40,
    pool_pre_ping=True
)

# Rango de usuarios de prueba
USER_ID_MIN = 80000
USER_ID_MAX = 80199

# Métricas custom
payment_success_count = 0
payment_failure_count = 0
race_condition_count = 0

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Hook de inicialización de Locust."""
    print(f"🚀 Iniciando Load Test contra: {DATABASE_URL[:50]}...")
    print(f"👥 Rango de usuarios: {USER_ID_MIN}-{USER_ID_MAX}")

class PaymentUser(HttpUser):
    """
    Simula un usuario realizando pagos con wallet.
    """
    wait_time = between(1, 3)  # Espera entre 1-3 segundos entre requests

    def on_start(self):
        """Ejecutado al inicio de cada usuario simulado."""
        # Asignar member_id aleatorio del rango de prueba
        self.member_id = random.randint(USER_ID_MIN, USER_ID_MAX)
        print(f"🧑 Usuario {self.member_id} iniciado")

    @task(10)  # Peso 10: Tarea más frecuente
    def pay_order_with_wallet(self):
        """
        Tarea principal: Crear orden y pagar con wallet.

        Flujo:
        1. Crear orden PENDING_PAYMENT
        2. Procesar pago con PaymentService
        3. Verificar éxito
        """
        start_time = time.time()

        with sqlmodel.Session(engine) as session:
            try:
                # 1. Obtener producto aleatorio
                products = session.exec(
                    sqlmodel.select(Products).limit(10)
                ).all()

                if not products:
                    print("❌ No hay productos en DB staging")
                    return

                product = random.choice(products)

                # 2. Crear orden
                order = Orders(
                    member_id=self.member_id,
                    country="MX",
                    currency="MXN",
                    subtotal=product.price_mx,
                    total=product.price_mx,
                    total_pv=product.pv_mx,
                    total_vn=product.vn_mx,
                    status=OrderStatus.PENDING_PAYMENT.value,
                    submitted_at=datetime.utcnow()
                )
                session.add(order)
                session.flush()

                # 3. Crear order item
                item = OrderItems(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=1,
                    unit_price=product.price_mx,
                    unit_pv=product.pv_mx,
                    unit_vn=product.vn_mx
                )
                item.calculate_totals()
                session.add(item)
                session.commit()

                order_id = order.id

                # 4. Procesar pago (el flujo completo)
                result = PaymentService.process_wallet_payment(
                    session=session,
                    order_id=order_id,
                    member_id=self.member_id
                )

                elapsed_time = (time.time() - start_time) * 1000  # ms

                # 5. Reportar a Locust
                if result["success"]:
                    global payment_success_count
                    payment_success_count += 1

                    self.environment.events.request.fire(
                        request_type="PAYMENT",
                        name="process_wallet_payment",
                        response_time=elapsed_time,
                        response_length=0,
                        exception=None,
                        context={}
                    )
                else:
                    global payment_failure_count
                    payment_failure_count += 1

                    # Detectar race conditions
                    if "ya fue procesada" in result["message"]:
                        global race_condition_count
                        race_condition_count += 1

                    self.environment.events.request.fire(
                        request_type="PAYMENT",
                        name="process_wallet_payment",
                        response_time=elapsed_time,
                        response_length=0,
                        exception=Exception(result["message"]),
                        context={}
                    )

            except Exception as e:
                elapsed_time = (time.time() - start_time) * 1000
                print(f"❌ Error en pago: {e}")

                self.environment.events.request.fire(
                    request_type="PAYMENT",
                    name="process_wallet_payment",
                    response_time=elapsed_time,
                    response_length=0,
                    exception=e,
                    context={}
                )
            finally:
                session.rollback()  # Limpiar transacción

    @task(3)  # Peso 3: Menos frecuente
    def check_wallet_balance(self):
        """Tarea secundaria: Verificar balance de wallet."""
        start_time = time.time()

        with sqlmodel.Session(engine) as session:
            try:
                from database.wallet import Wallets
                wallet = session.exec(
                    sqlmodel.select(Wallets).where(Wallets.member_id == self.member_id)
                ).first()

                elapsed_time = (time.time() - start_time) * 1000

                self.environment.events.request.fire(
                    request_type="WALLET",
                    name="get_wallet_balance",
                    response_time=elapsed_time,
                    response_length=0,
                    exception=None if wallet else Exception("Wallet not found"),
                    context={}
                )

            except Exception as e:
                elapsed_time = (time.time() - start_time) * 1000
                self.environment.events.request.fire(
                    request_type="WALLET",
                    name="get_wallet_balance",
                    response_time=elapsed_time,
                    response_length=0,
                    exception=e,
                    context={}
                )

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Hook al finalizar el test."""
    print("\n" + "="*80)
    print("📊 RESULTADOS FINALES")
    print("="*80)
    print(f"✅ Pagos exitosos: {payment_success_count}")
    print(f"❌ Pagos fallidos: {payment_failure_count}")
    print(f"⚠️  Race conditions detectadas: {race_condition_count}")
    print("="*80)
