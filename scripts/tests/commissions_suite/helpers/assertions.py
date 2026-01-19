"""
Custom Assertions para Testing de Comisiones MLM

Proporciona funciones helper para validaciones comunes en tests.

Autor: QA Engineer Giovann
Fecha: Octubre 2025
"""

from typing import Optional, List
from sqlmodel import Session, select

from database.comissions import Commissions, BonusType
from database.user_rank_history import UserRankHistory
from database.wallet import Wallets, WalletTransactions


def assert_commission_exists(
    session: Session,
    member_id: int,
    bonus_type: str,
    expected_amount: Optional[float] = None,
    tolerance: float = 0.01,
    level_depth: Optional[int] = None
) -> Commissions:
    """
    Valida que una comisión existe y tiene los valores esperados.

    Args:
        session: Sesión de BD
        member_id: ID del receptor
        bonus_type: Tipo de bono (BonusType enum value)
        expected_amount: Monto esperado (opcional)
        tolerance: Tolerancia para comparación (default 0.01)
        level_depth: Nivel esperado (opcional)

    Returns:
        Comisión encontrada

    Raises:
        AssertionError si no se encuentra o valores incorrectos
    """
    # Buscar comisión
    query = select(Commissions).where(
        (Commissions.member_id == member_id) &
        (Commissions.bonus_type == bonus_type)
    )

    if level_depth is not None:
        query = query.where(Commissions.level_depth == level_depth)

    commission = session.exec(query).first()

    # Validar existencia
    assert commission is not None, \
        f"No se encontró comisión {bonus_type} para member_id={member_id}" + \
        (f" nivel={level_depth}" if level_depth else "")

    # Validar monto si se proporciona
    if expected_amount is not None:
        actual_amount = commission.amount_converted
        assert abs(actual_amount - expected_amount) <= tolerance, \
            f"Monto incorrecto: esperado {expected_amount:.2f}, obtenido {actual_amount:.2f}"

    return commission


def assert_commission_not_exists(
    session: Session,
    member_id: int,
    bonus_type: str,
    level_depth: Optional[int] = None
):
    """
    Valida que NO existe una comisión.

    Args:
        session: Sesión de BD
        member_id: ID del receptor
        bonus_type: Tipo de bono
        level_depth: Nivel específico (opcional)

    Raises:
        AssertionError si la comisión existe
    """
    query = select(Commissions).where(
        (Commissions.member_id == member_id) &
        (Commissions.bonus_type == bonus_type)
    )

    if level_depth is not None:
        query = query.where(Commissions.level_depth == level_depth)

    commission = session.exec(query).first()

    assert commission is None, \
        f"Se encontró comisión {bonus_type} para member_id={member_id} pero NO debería existir"


def assert_total_commissions_count(
    session: Session,
    member_id: int,
    bonus_type: str,
    expected_count: int
):
    """
    Valida el total de comisiones de un tipo para un usuario.

    Args:
        session: Sesión de BD
        member_id: ID del receptor
        bonus_type: Tipo de bono
        expected_count: Cantidad esperada

    Raises:
        AssertionError si la cantidad no coincide
    """
    commissions = session.exec(
        select(Commissions).where(
            (Commissions.member_id == member_id) &
            (Commissions.bonus_type == bonus_type)
        )
    ).all()

    actual_count = len(commissions)
    assert actual_count == expected_count, \
        f"Cantidad incorrecta: esperado {expected_count} comisiones, obtenido {actual_count}"


def assert_commission_percentage(
    session: Session,
    member_id: int,
    bonus_type: str,
    base_amount: float,
    expected_percentage: float,
    tolerance: float = 0.01
) -> Commissions:
    """
    Valida que una comisión tiene el porcentaje correcto del monto base.

    Args:
        session: Sesión de BD
        member_id: ID del receptor
        bonus_type: Tipo de bono
        base_amount: Monto base (PV o VN)
        expected_percentage: Porcentaje esperado (0.30 = 30%)
        tolerance: Tolerancia para comparación

    Returns:
        Comisión encontrada

    Raises:
        AssertionError si el porcentaje no coincide
    """
    commission = assert_commission_exists(session, member_id, bonus_type)

    expected_amount = base_amount * expected_percentage
    actual_amount = commission.amount_vn

    assert abs(actual_amount - expected_amount) <= tolerance, \
        f"Porcentaje incorrecto: esperado {expected_percentage*100}% de {base_amount} = {expected_amount:.2f}, " \
        f"obtenido {actual_amount:.2f}"

    return commission


def assert_currency_conversion(
    session: Session,
    commission_id: int,
    expected_origin_currency: str,
    expected_destination_currency: str
):
    """
    Valida la conversión de moneda en una comisión.

    Args:
        session: Sesión de BD
        commission_id: ID de la comisión
        expected_origin_currency: Moneda origen esperada
        expected_destination_currency: Moneda destino esperada

    Raises:
        AssertionError si las monedas no coinciden
    """
    commission = session.get(Commissions, commission_id)
    assert commission is not None, f"Comisión {commission_id} no encontrada"

    assert commission.currency_origin == expected_origin_currency, \
        f"Moneda origen incorrecta: esperado {expected_origin_currency}, " \
        f"obtenido {commission.currency_origin}"

    assert commission.currency_destination == expected_destination_currency, \
        f"Moneda destino incorrecta: esperado {expected_destination_currency}, " \
        f"obtenido {commission.currency_destination}"

    # Validar que amount_converted > 0 si hay conversión
    if expected_origin_currency != expected_destination_currency:
        assert commission.amount_converted > 0, \
            "amount_converted debe ser > 0 cuando hay conversión de moneda"


def assert_rank_achieved(
    session: Session,
    member_id: int,
    expected_rank_id: int
) -> UserRankHistory:
    """
    Valida que un usuario alcanzó un rango específico.

    Args:
        session: Sesión de BD
        member_id: ID del usuario
        expected_rank_id: ID del rango esperado

    Returns:
        Registro de UserRankHistory

    Raises:
        AssertionError si el rango no coincide
    """
    # Obtener último rango
    rank_history = session.exec(
        select(UserRankHistory)
        .where(UserRankHistory.member_id == member_id)
        .order_by(UserRankHistory.achieved_on.desc())
    ).first()

    assert rank_history is not None, \
        f"No se encontró historial de rangos para member_id={member_id}"

    assert rank_history.rank_id == expected_rank_id, \
        f"Rango incorrecto: esperado {expected_rank_id}, obtenido {rank_history.rank_id}"

    return rank_history


def assert_wallet_balance(
    session: Session,
    member_id: int,
    expected_balance: float,
    tolerance: float = 0.01
) -> Wallets:
    """
    Valida el balance de una wallet.

    Args:
        session: Sesión de BD
        member_id: ID del usuario
        expected_balance: Balance esperado
        tolerance: Tolerancia para comparación

    Returns:
        Wallet

    Raises:
        AssertionError si el balance no coincide
    """
    wallet = session.exec(
        select(Wallets).where(Wallets.member_id == member_id)
    ).first()

    assert wallet is not None, f"No se encontró wallet para member_id={member_id}"

    actual_balance = wallet.balance
    assert abs(actual_balance - expected_balance) <= tolerance, \
        f"Balance incorrecto: esperado {expected_balance:.2f}, obtenido {actual_balance:.2f}"

    return wallet


def assert_wallet_transaction_exists(
    session: Session,
    member_id: int,
    transaction_type: str,
    expected_amount: Optional[float] = None,
    tolerance: float = 0.01
) -> WalletTransactions:
    """
    Valida que existe una transacción de wallet.

    Args:
        session: Sesión de BD
        member_id: ID del usuario
        transaction_type: Tipo de transacción
        expected_amount: Monto esperado (opcional)
        tolerance: Tolerancia para comparación

    Returns:
        Transacción encontrada

    Raises:
        AssertionError si no se encuentra o monto incorrecto
    """
    transaction = session.exec(
        select(WalletTransactions).where(
            (WalletTransactions.member_id == member_id) &
            (WalletTransactions.transaction_type == transaction_type)
        )
    ).first()

    assert transaction is not None, \
        f"No se encontró transacción {transaction_type} para member_id={member_id}"

    if expected_amount is not None:
        actual_amount = abs(transaction.amount)  # Usar abs para débitos negativos
        assert abs(actual_amount - abs(expected_amount)) <= tolerance, \
            f"Monto incorrecto: esperado {expected_amount:.2f}, obtenido {transaction.amount:.2f}"

    return transaction


def assert_commissions_sum_equals(
    session: Session,
    member_id: int,
    bonus_type: str,
    expected_total: float,
    tolerance: float = 0.01
):
    """
    Valida que la suma de comisiones de un tipo es igual al esperado.

    Args:
        session: Sesión de BD
        member_id: ID del receptor
        bonus_type: Tipo de bono
        expected_total: Total esperado
        tolerance: Tolerancia para comparación

    Raises:
        AssertionError si el total no coincide
    """
    commissions = session.exec(
        select(Commissions).where(
            (Commissions.member_id == member_id) &
            (Commissions.bonus_type == bonus_type)
        )
    ).all()

    actual_total = sum(c.amount_converted for c in commissions)

    assert abs(actual_total - expected_total) <= tolerance, \
        f"Total de comisiones incorrecto: esperado {expected_total:.2f}, obtenido {actual_total:.2f}"


def assert_decimal_precision(value: float, decimals: int = 2):
    """
    Valida que un valor tiene la precisión decimal esperada.

    Args:
        value: Valor a validar
        decimals: Cantidad de decimales esperados

    Raises:
        AssertionError si la precisión no coincide
    """
    str_value = f"{value:.{decimals}f}"
    reconstructed = float(str_value)

    assert abs(value - reconstructed) < 10**(-decimals), \
        f"Precisión decimal incorrecta: valor {value} excede {decimals} decimales"


def get_all_commissions(
    session: Session,
    member_id: int,
    bonus_type: Optional[str] = None
) -> List[Commissions]:
    """
    Obtiene todas las comisiones de un usuario.

    Args:
        session: Sesión de BD
        member_id: ID del receptor
        bonus_type: Tipo de bono (opcional, None = todos)

    Returns:
        Lista de comisiones
    """
    query = select(Commissions).where(Commissions.member_id == member_id)

    if bonus_type is not None:
        query = query.where(Commissions.bonus_type == bonus_type)

    return list(session.exec(query).all())


def print_commissions_debug(
    session: Session,
    member_id: int,
    bonus_type: Optional[str] = None
):
    """
    Helper para debug: imprime todas las comisiones de un usuario.

    Args:
        session: Sesión de BD
        member_id: ID del receptor
        bonus_type: Tipo de bono (opcional)
    """
    commissions = get_all_commissions(session, member_id, bonus_type)

    print(f"\n===== COMISIONES DE member_id={member_id} =====")
    print(f"Total comisiones: {len(commissions)}")

    for i, comm in enumerate(commissions, 1):
        print(f"\n--- Comisión {i} ---")
        print(f"  ID: {comm.id}")
        print(f"  Tipo: {comm.bonus_type}")
        print(f"  Nivel: {comm.level_depth}")
        print(f"  Monto VN: {comm.amount_vn:.2f}")
        print(f"  Monto Convertido: {comm.amount_converted:.2f}")
        print(f"  Moneda Origen: {comm.currency_origin}")
        print(f"  Moneda Destino: {comm.currency_destination}")
        print(f"  Source Member: {comm.source_member_id}")
        print(f"  Source Order: {comm.source_order_id}")

    print(f"\n===== FIN COMISIONES =====\n")
