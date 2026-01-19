"""
Configuración global de pytest para testing del sistema de comisiones MLM.
Define fixtures compartidas y configuración base.

Autor: QA Engineer Giovann
Fecha: Octubre 2025
"""

import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional
from sqlmodel import Session, create_engine, SQLModel, select
from sqlalchemy.pool import StaticPool

# Agregar path del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Importar directamente de los archivos para evitar conflictos de metaclases
from database.users import Users, UserStatus
from database.products import Products, ProductType, ProductPresentation
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.ranks import Ranks
from database.periods import Periods
from database.usertreepaths import UserTreePath
from database.user_rank_history import UserRankHistory
from database.comissions import Commissions, BonusType
from database.wallet import Wallets
from database.exchange_rates import ExchangeRates

from NNProtect_new_website.modules.network.backend.genealogy_service import GenealogyService


# ==================== DATABASE SETUP ====================

@pytest.fixture(scope="session")
def engine():
    """
    Engine de BD en memoria para tests (session-scoped).
    Se crea UNA VEZ para toda la sesión de testing.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Crear todas las tablas
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup al final de la sesión
    engine.dispose()


@pytest.fixture
def db_session(engine):
    """
    Sesión de BD limpia para cada test (function-scoped).
    Hace rollback automático al finalizar cada test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Rollback para limpiar datos de prueba
    session.close()
    transaction.rollback()
    connection.close()


# ==================== RANK FIXTURES ====================

@pytest.fixture(scope="session")
def setup_ranks(engine):
    """
    Carga los 9 rangos del sistema (session-scoped).
    Se ejecuta UNA VEZ al inicio de la sesión.
    """
    with Session(engine) as session:
        ranks_data = [
            {"id": 1, "name": "Sin rango", "pvg_required": 0},
            {"id": 2, "name": "Visionario", "pvg_required": 1465},
            {"id": 3, "name": "Emprendedor", "pvg_required": 21000},
            {"id": 4, "name": "Creativo", "pvg_required": 58000},
            {"id": 5, "name": "Innovador", "pvg_required": 120000},
            {"id": 6, "name": "Embajador Transformador", "pvg_required": 300000},
            {"id": 7, "name": "Embajador Inspirador", "pvg_required": 650000},
            {"id": 8, "name": "Embajador Consciente", "pvg_required": 1300000},
            {"id": 9, "name": "Embajador Solidario", "pvg_required": 2900000},
        ]

        for rank_data in ranks_data:
            rank = Ranks(**rank_data)
            session.add(rank)

        session.commit()

    return ranks_data


@pytest.fixture
def ranks(db_session, setup_ranks):
    """
    Retorna diccionario de rangos disponibles para el test.
    """
    ranks_dict = {}
    for rank in setup_ranks:
        db_rank = db_session.exec(
            select(Ranks).where(Ranks.id == rank["id"])
        ).first()
        ranks_dict[rank["name"]] = db_rank

    return ranks_dict


# ==================== PERIOD FIXTURES ====================

@pytest.fixture
def test_period_current(db_session):
    """
    Crea período actual de prueba (Octubre 2025).
    """
    period = Periods(
        name="Test Period Oct 2025",
        starts_on=datetime(2025, 10, 1, tzinfo=timezone.utc),
        ends_on=datetime(2025, 10, 31, 23, 59, 59, tzinfo=timezone.utc),
        closed_at=None  # Período activo
    )
    db_session.add(period)
    db_session.flush()

    return period


@pytest.fixture
def test_period_closed(db_session):
    """
    Crea período cerrado de prueba (Septiembre 2025).
    """
    period = Periods(
        name="Test Period Sep 2025",
        starts_on=datetime(2025, 9, 1, tzinfo=timezone.utc),
        ends_on=datetime(2025, 9, 30, 23, 59, 59, tzinfo=timezone.utc),
        closed_at=datetime(2025, 9, 30, 23, 59, 59, tzinfo=timezone.utc)
    )
    db_session.add(period)
    db_session.flush()

    return period


# ==================== USER FIXTURES ====================

@pytest.fixture
def create_test_user(db_session):
    """
    Factory fixture para crear usuarios de prueba.

    Uso:
        user_a = create_test_user(member_id=1000, sponsor_id=None, country="Mexico")
    """
    def _create_user(
        member_id: int,
        sponsor_id: Optional[int] = None,
        country: str = "Mexico",
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        pv_cache: int = 0,
        pvg_cache: int = 0
    ) -> Users:
        user = Users(
            member_id=member_id,
            sponsor_id=sponsor_id,
            first_name=first_name or f"User_{member_id}",
            last_name=last_name or "Test",
            email=email or f"user{member_id}@test.com",
            country=country,
            country_cache=country,
            pv_cache=pv_cache,
            pvg_cache=pvg_cache,
            created_at=datetime.now(timezone.utc)
        )

        db_session.add(user)
        db_session.flush()

        # Agregar a genealogía
        GenealogyService.add_member_to_tree(db_session, member_id, sponsor_id)

        # Asignar rango inicial "Sin rango"
        rank_history = UserRankHistory(
            member_id=member_id,
            rank_id=1,  # Sin rango
            achieved_on=datetime.now(timezone.utc),
            period_id=None
        )
        db_session.add(rank_history)
        db_session.flush()

        return user

    return _create_user


@pytest.fixture
def test_network_simple(create_test_user):
    """
    Crea red simple de 3 niveles: A → B → C

    Retorna:
        {'A': Users, 'B': Users, 'C': Users}
    """
    user_a = create_test_user(member_id=1000, sponsor_id=None, country="Mexico")
    user_b = create_test_user(member_id=1001, sponsor_id=1000, country="Mexico")
    user_c = create_test_user(member_id=1002, sponsor_id=1001, country="Mexico")

    return {'A': user_a, 'B': user_b, 'C': user_c}


@pytest.fixture
def test_network_4_levels(create_test_user):
    """
    Crea red de 4 niveles: A → B → C → D

    Retorna:
        {'A': Users, 'B': Users, 'C': Users, 'D': Users}
    """
    user_a = create_test_user(member_id=1000, sponsor_id=None, country="Mexico")
    user_b = create_test_user(member_id=1001, sponsor_id=1000, country="Mexico")
    user_c = create_test_user(member_id=1002, sponsor_id=1001, country="Mexico")
    user_d = create_test_user(member_id=1003, sponsor_id=1002, country="Mexico")

    return {'A': user_a, 'B': user_b, 'C': user_c, 'D': user_d}


@pytest.fixture
def test_network_multi_country(create_test_user):
    """
    Crea red multi-país: A(MX) → B(USA) → C(COL)
    """
    user_a = create_test_user(member_id=1000, sponsor_id=None, country="Mexico")
    user_b = create_test_user(member_id=1001, sponsor_id=1000, country="USA")
    user_c = create_test_user(member_id=1002, sponsor_id=1001, country="Colombia")

    return {'A': user_a, 'B': user_b, 'C': user_c}


# ==================== PRODUCT FIXTURES ====================

@pytest.fixture
def test_kit_full_protect(db_session):
    """
    Kit Full Protect - Genera PV Y VN (CORREGIDO).
    ✅ Kits pagan Bono Rápido pero NO Uninivel.
    """
    product = Products(
        SKU="KIT-FULL-TEST",
        product_name="Full Protect Kit (Test)",
        description="Kit completo de protección",
        presentation="kit",
        type="suplemento",  # type es la categoría, NO indica si es kit
        # México
        pv_mx=2930,
        vn_mx=2930,  # ✅ CORREGIDO: Kits SÍ generan VN
        price_mx=5790,
        public_mx=7900,
        # USA
        pv_usa=2930,
        vn_usa=2930,
        price_usa=320,
        public_usa=440,
        # Colombia
        pv_colombia=2930,
        vn_colombia=2930,
        price_colombia=1300000,
        public_colombia=1800000,
        is_new=False
    )

    db_session.add(product)
    db_session.flush()

    return product


@pytest.fixture
def test_product_dna_60(db_session):
    """
    Producto DNA 60 Cápsulas - Genera PV y VN.
    ✅ Productos regulares pagan todos los bonos (Directo, Uninivel).
    ❌ Productos regulares NO pagan Bono Rápido.
    """
    product = Products(
        SKU="DNA-60-TEST",
        product_name="DNA 60 Cápsulas (Test)",
        description="Suplemento DNA",
        presentation="cápsulas",  # Usar valor correcto del enum
        type="suplemento",
        # México
        pv_mx=1465,
        vn_mx=1465,  # ✅ Productos SÍ generan VN
        price_mx=2490,
        public_mx=3400,
        # USA
        pv_usa=1465,
        vn_usa=1465,
        price_usa=138,
        public_usa=188,
        # Colombia
        pv_colombia=1465,
        vn_colombia=1465,
        price_colombia=555000,
        public_colombia=766000,
        is_new=True
    )

    db_session.add(product)
    db_session.flush()

    return product


# ==================== ORDER FIXTURES ====================

@pytest.fixture
def create_test_order(db_session, test_period_current):
    """
    Factory fixture para crear órdenes de prueba.

    Uso:
        order = create_test_order(
            member_id=1001,
            items=[(product_kit, 1), (product_dna, 2)],
            payment_confirmed=True
        )
    """
    def _create_order(
        member_id: int,
        items: List[Tuple[Products, int]],  # (product, quantity)
        country: str = "Mexico",
        payment_confirmed: bool = True,
        payment_confirmed_at: Optional[datetime] = None
    ) -> Orders:
        # Determinar moneda por país
        currency_map = {"Mexico": "MXN", "USA": "USD", "Colombia": "COP"}
        currency = currency_map.get(country, "MXN")

        # Crear orden
        order = Orders(
            member_id=member_id,
            country=country,
            currency=currency,
            status=OrderStatus.PAYMENT_CONFIRMED.value if payment_confirmed else OrderStatus.DRAFT.value,
            created_at=datetime.now(timezone.utc),
            submitted_at=datetime.now(timezone.utc) if payment_confirmed else None,
            payment_confirmed_at=payment_confirmed_at or (datetime.now(timezone.utc) if payment_confirmed else None),
            period_id=test_period_current.id if payment_confirmed else None
        )

        # Calcular totales
        subtotal = 0
        total_pv = 0
        total_vn = 0

        for product, quantity in items:
            # Obtener precio según país
            if country == "Mexico":
                price = product.price_mx
                pv = product.pv_mx
                vn = product.vn_mx
            elif country == "USA":
                price = product.price_usa
                pv = product.pv_usa
                vn = product.vn_usa
            elif country == "Colombia":
                price = product.price_colombia
                pv = product.pv_colombia
                vn = product.vn_colombia
            else:
                price = product.price_mx
                pv = product.pv_mx
                vn = product.vn_mx

            subtotal += price * quantity
            total_pv += pv * quantity
            total_vn += vn * quantity

        order.subtotal = subtotal
        order.shipping_cost = 0
        order.tax = 0
        order.discount = 0
        order.total = subtotal
        order.total_pv = total_pv
        order.total_vn = total_vn

        db_session.add(order)
        db_session.flush()

        # Crear order items
        for product, quantity in items:
            if country == "Mexico":
                price = product.price_mx
                pv = product.pv_mx
                vn = product.vn_mx
            elif country == "USA":
                price = product.price_usa
                pv = product.pv_usa
                vn = product.vn_usa
            elif country == "Colombia":
                price = product.price_colombia
                pv = product.pv_colombia
                vn = product.vn_colombia
            else:
                price = product.price_mx
                pv = product.pv_mx
                vn = product.vn_mx

            item = OrderItems(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=price,
                line_total=price * quantity,
                unit_pv=pv,
                line_pv=pv * quantity,
                unit_vn=vn,
                line_vn=vn * quantity
            )
            db_session.add(item)

        db_session.flush()

        return order

    return _create_order


# ==================== WALLET FIXTURES ====================

@pytest.fixture
def create_test_wallet(db_session):
    """
    Factory fixture para crear wallets de prueba.
    """
    def _create_wallet(member_id: int, currency: str = "MXN", balance: float = 0.0) -> Wallets:
        wallet = Wallets(
            member_id=member_id,
            balance=balance,
            currency=currency,
            status="active"
        )
        db_session.add(wallet)
        db_session.flush()
        return wallet

    return _create_wallet


# ==================== EXCHANGE RATE FIXTURES ====================

@pytest.fixture
def setup_exchange_rates(db_session):
    """
    Configura tasas de cambio fijas para pruebas.
    """
    rates = [
        # MXN ↔ USD
        ExchangeRates(
            from_currency="MXN",
            to_currency="USD",
            rate=0.055,  # 1 MXN = 0.055 USD
            effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_until=None,
            notes="Test rate MXN → USD"
        ),
        ExchangeRates(
            from_currency="USD",
            to_currency="MXN",
            rate=18.0,  # 1 USD = 18 MXN
            effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_until=None,
            notes="Test rate USD → MXN"
        ),
        # MXN ↔ COP
        ExchangeRates(
            from_currency="MXN",
            to_currency="COP",
            rate=225.0,  # 1 MXN = 225 COP
            effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_until=None,
            notes="Test rate MXN → COP"
        ),
        ExchangeRates(
            from_currency="COP",
            to_currency="MXN",
            rate=0.0044,  # 1 COP = 0.0044 MXN
            effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_until=None,
            notes="Test rate COP → MXN"
        ),
        # USD ↔ COP
        ExchangeRates(
            from_currency="USD",
            to_currency="COP",
            rate=4000.0,  # 1 USD = 4000 COP
            effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_until=None,
            notes="Test rate USD → COP"
        ),
        ExchangeRates(
            from_currency="COP",
            to_currency="USD",
            rate=0.00025,  # 1 COP = 0.00025 USD
            effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_until=None,
            notes="Test rate COP → USD"
        ),
    ]

    for rate in rates:
        db_session.add(rate)

    db_session.flush()

    return rates


# ==================== ASSERTION HELPERS ====================

def assert_commission_created(
    db_session: Session,
    member_id: int,
    bonus_type: str,
    expected_amount: float,
    tolerance: float = 0.01
) -> Commissions:
    """
    Helper para validar que una comisión fue creada correctamente.

    Args:
        db_session: Sesión de BD
        member_id: ID del receptor
        bonus_type: Tipo de bono
        expected_amount: Monto esperado
        tolerance: Tolerancia para comparación (default 0.01)

    Returns:
        Comisión encontrada

    Raises:
        AssertionError si no se encuentra o monto incorrecto
    """
    commission = db_session.exec(
        select(Commissions).where(
            (Commissions.member_id == member_id) &
            (Commissions.bonus_type == bonus_type)
        )
    ).first()

    assert commission is not None, f"No se encontró comisión {bonus_type} para member_id={member_id}"
    assert abs(commission.amount_converted - expected_amount) <= tolerance, \
        f"Monto incorrecto: esperado {expected_amount}, obtenido {commission.amount_converted}"

    return commission


def assert_no_commission_created(
    db_session: Session,
    member_id: int,
    bonus_type: str
):
    """
    Helper para validar que NO se creó una comisión.
    """
    commission = db_session.exec(
        select(Commissions).where(
            (Commissions.member_id == member_id) &
            (Commissions.bonus_type == bonus_type)
        )
    ).first()

    assert commission is None, f"Se creó comisión {bonus_type} para member_id={member_id} pero no debería"
