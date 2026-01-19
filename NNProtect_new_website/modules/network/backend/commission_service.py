"""
Servicio POO para cálculo y registro de comisiones MLM.
Implementa Bono Rápido y otros bonos del plan de compensación.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import sqlmodel
from typing import Optional, List
from datetime import datetime, timezone

from database.users import Users
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.products import Products
from database.comissions import Commissions, BonusType
from database.periods import Periods
from database.ranks import Ranks
from database.usertreepaths import UserTreePath
from .genealogy_service import GenealogyService
from NNProtect_new_website.modules.finance.backend.exchange_service import ExchangeService
from .rank_service import RankService


class CommissionService:
    """
    Servicio POO para gestión de comisiones MLM.
    Principio POO: Encapsula toda la lógica de cálculo de comisiones.
    """

    # Porcentajes del Bono Rápido por nivel (basados en PV del kit)
    FAST_START_BONUS_PERCENTAGES = {
        1: 0.30,  # Nivel 1: 30% del PV
        2: 0.10,  # Nivel 2: 10% del PV
        3: 0.05   # Nivel 3: 5% del PV
    }

    # Porcentajes del Bono Uninivel por rango (MLM_SCHEME_README.md líneas 369-380)
    UNILEVEL_BONUS_PERCENTAGES = {
        "Visionario": [5, 8, 10],
        "Emprendedor": [5, 8, 10, 10],
        "Creativo": [5, 8, 10, 10, 5],
        "Innovador": [5, 8, 10, 10, 5, 4],
        "Embajador Transformador": [5, 8, 10, 10, 5, 4, 4, 3, 3, 0.5],
        "Embajador Inspirador": [5, 8, 10, 10, 5, 4, 4, 3, 3, 1.0],
        "Embajador Consciente": [5, 8, 10, 10, 5, 4, 4, 3, 3, 1.5],
        "Embajador Solidario": [5, 8, 10, 10, 5, 4, 4, 3, 3, 2.0]
    }

    # Porcentajes del Bono Matching por rango (MLM_SCHEME_README.md líneas 622-629)
    MATCHING_BONUS_PERCENTAGES = {
        "Embajador Transformador": [30],
        "Embajador Inspirador": [30, 20],
        "Embajador Consciente": [30, 20, 10],
        "Embajador Solidario": [30, 20, 10, 5]
    }

    # Rangos Embajador elegibles para Matching Bonus
    AMBASSADOR_RANKS = [
        "Embajador Transformador",
        "Embajador Inspirador",
        "Embajador Consciente",
        "Embajador Solidario"
    ]

    # Montos del Bono por Alcance por rango (MLM_SCHEME_README.md líneas 540-550)
    ACHIEVEMENT_BONUS_AMOUNTS = {
        "Emprendedor": {"MXN": 1500, "USD": 85, "COP": 330000},
        "Creativo": {"MXN": 3000, "USD": 165, "COP": 666000},
        "Innovador": {"MXN": 5000, "USD": 280, "COP": 1100000},
        "Embajador Transformador": {"MXN": 7500, "USD": 390, "COP": 1650000},
        "Embajador Inspirador": {"MXN": 10000, "USD": 555, "COP": 2220000},
        "Embajador Consciente": {"MXN": 20000, "USD": 1111, "COP": 4400000},
        "Embajador Solidario": {"MXN": 40000, "USD": 2222, "COP": 8800000}
    }

    @classmethod
    def process_fast_start_bonus(cls, session, order_id: int) -> List[int]:
        """
        Procesa Bono Rápido cuando se confirma el pago de un KIT.
        Reglas:
        - Solo aplica para productos tipo 'kit'
        - Paga 30%/10%/5% del PV del kit a niveles 1/2/3
        - Se calcula en PV y se convierte a la moneda del patrocinador

        Principio KISS: Lógica directa y clara.

        Args:
            session: Sesión de base de datos
            order_id: ID de la orden confirmada

        Returns:
            Lista de IDs de comisiones creadas
        """
        try:
            # 1. Verificar que la orden existe y está confirmada
            order = session.exec(
                sqlmodel.select(Orders).where(Orders.id == order_id)
            ).first()

            if not order:
                print(f"❌ Orden {order_id} no encontrada")
                return []

            if order.status != OrderStatus.PAYMENT_CONFIRMED.value:
                print(f"⚠️  Orden {order_id} no está confirmada")
                return []

            # 2. Obtener items de la orden
            order_items = session.exec(
                sqlmodel.select(OrderItems).where(OrderItems.order_id == order_id)
            ).all()

            if not order_items:
                print(f"⚠️  Orden {order_id} no tiene items")
                return []

            # 3. Filtrar solo kits (por presentation, NO por type)
            kit_items = []
            for item in order_items:
                product = session.exec(
                    sqlmodel.select(Products).where(Products.id == item.product_id)
                ).first()

                if product and product.presentation == "kit":
                    kit_items.append((item, product))

            if not kit_items:
                print(f"⚠️  Orden {order_id} no contiene kits")
                return []

            # 4. Obtener upline del comprador (niveles 1, 2, 3)
            buyer_id = order.member_id
            upline = GenealogyService.get_upline(session, buyer_id, max_depth=3)

            if not upline:
                print(f"⚠️  Comprador {buyer_id} no tiene upline")
                return []

            # 5. Crear comisiones por cada kit
            commission_ids = []

            for item, product in kit_items:
                # PV base del kit
                kit_pv = item.line_pv  # PV total del item (unit_pv * quantity)

                # Procesar upline nivel por nivel
                for level, sponsor_user in enumerate(upline[:3], start=1):
                    percentage = cls.FAST_START_BONUS_PERCENTAGES.get(level, 0)

                    if percentage == 0:
                        continue

                    # Calcular comisión en PV
                    commission_pv = kit_pv * percentage

                    # sponsor_user ya es un objeto Users de get_upline()
                    sponsor_member_id = sponsor_user.member_id

                    # Obtener moneda del comprador (origen) y patrocinador (destino)
                    buyer_currency = ExchangeService.get_country_currency(order.country)
                    sponsor_currency = ExchangeService.get_country_currency(sponsor_user.country_cache or sponsor_user.country_cache)

                    # Convertir PV a VN en la moneda del patrocinador
                    # Si ambos tienen la misma moneda, no hay conversión
                    commission_vn = ExchangeService.convert_amount(
                        session,
                        amount=commission_pv,
                        from_currency=buyer_currency,
                        to_currency=sponsor_currency,
                        as_of_date=order.payment_confirmed_at
                    )

                    # Obtener período actual
                    period = cls._get_current_period(session)

                    # Crear registro de comisión
                    commission = Commissions(
                        member_id=sponsor_member_id,
                        bonus_type=BonusType.BONO_RAPIDO.value,
                        source_member_id=buyer_id,
                        source_order_id=order_id,
                        period_id=period.id if period else None,
                        level_depth=level,
                        amount_vn=commission_pv,
                        currency_origin=buyer_currency,
                        amount_converted=commission_vn,
                        currency_destination=sponsor_currency,
                        exchange_rate=1.0,  # TODO: Get actual exchange rate
                        calculated_at=datetime.now(timezone.utc),
                        paid_at=None,
                        notes=f"Bono Rápido {percentage*100:.0f}% - Kit: {product.product_name} ({kit_pv} PV)"
                    )

                    session.add(commission)
                    session.flush()
                    commission_ids.append(commission.id)

                    print(f"✅ Comisión Bono Rápido creada: ${commission_vn:.2f} para member_id={sponsor_member_id} (nivel {level})")

            return commission_ids

        except Exception as e:
            print(f"❌ Error procesando Bono Rápido para orden {order_id}: {e}")
            return []

    @classmethod
    def process_direct_bonus(
        cls,
        session,
        buyer_id: int,
        order_id: int,
        vn_amount: float
    ) -> Optional[int]:
        """
        Procesa Bono Directo (25% del VN) al patrocinador directo.
        Reglas:
        - Solo aplica si hay patrocinador directo (sponsor_id)
        - 25% del VN total de la orden
        - Se paga en la moneda del patrocinador
        - Aplica tanto para kits como productos regulares

        Principio KISS: Cálculo directo y simple.

        Args:
            session: Sesión de base de datos
            buyer_id: ID del comprador (source)
            order_id: ID de la orden
            vn_amount: Monto total de VN de la orden

        Returns:
            ID de la comisión creada, o None si no aplica
        """
        try:
            # 1. Obtener comprador
            buyer = session.exec(
                sqlmodel.select(Users).where(Users.member_id == buyer_id)
            ).first()

            if not buyer:
                print(f"❌ Comprador {buyer_id} no encontrado")
                return None

            # 2. Verificar que tenga patrocinador
            if not buyer.sponsor_id:
                print(f"⚠️  Comprador {buyer_id} no tiene patrocinador directo")
                return None

            # 3. Obtener patrocinador
            sponsor = session.exec(
                sqlmodel.select(Users).where(Users.member_id == buyer.sponsor_id)
            ).first()

            if not sponsor:
                print(f"❌ Patrocinador {buyer.sponsor_id} no encontrado")
                return None

            # 4. Calcular comisión (25% del VN)
            DIRECT_BONUS_PERCENTAGE = 0.25
            commission_vn = vn_amount * DIRECT_BONUS_PERCENTAGE

            # 5. Obtener monedas
            buyer_currency = ExchangeService.get_country_currency(buyer.country_cache)
            sponsor_currency = ExchangeService.get_country_currency(sponsor.country_cache)

            # 6. Convertir a moneda del patrocinador si es necesario
            order = session.exec(
                sqlmodel.select(Orders).where(Orders.id == order_id)
            ).first()

            commission_converted = ExchangeService.convert_amount(
                session=session,
                amount=commission_vn,
                from_currency=buyer_currency,
                to_currency=sponsor_currency,
                as_of_date=order.payment_confirmed_at if order else datetime.now(timezone.utc)
            )

            # 7. Obtener período actual
            period = cls._get_current_period(session)

            # 8. Crear registro de comisión
            commission = Commissions(
                member_id=sponsor.member_id,
                bonus_type=BonusType.BONO_DIRECTO.value,
                source_member_id=buyer_id,
                source_order_id=order_id,
                period_id=period.id if period else None,
                level_depth=1,  # Siempre nivel 1 (directo)
                amount_vn=commission_vn,
                currency_origin=buyer_currency,
                amount_converted=commission_converted,
                currency_destination=sponsor_currency,
                exchange_rate=1.0,  # TODO: Get actual exchange rate
                calculated_at=datetime.now(timezone.utc),
                paid_at=None,
                notes=f"Bono Directo 25% VN - Orden #{order_id}"
            )

            session.add(commission)
            session.flush()

            print(f"✅ Bono Directo creado: {commission_converted:.2f} {sponsor_currency} para sponsor {sponsor.member_id}")

            return commission.id

        except Exception as e:
            print(f"❌ Error procesando Bono Directo para orden {order_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def calculate_unilevel_bonus(cls, session, member_id: int, period_id: int) -> List[int]:
        """
        Calcula el Bono Uninivel mensual para un miembro.
        Reglas:
        - Solo productos regulares (NO kits) generan VN para Uninivel
        - Porcentajes según rango del miembro
        - Embajadores tienen nivel 10+ infinito

        Principio KISS: Lógica clara por nivel.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro
            period_id: ID del período mensual

        Returns:
            Lista de IDs de comisiones creadas
        """
        try:
            # 1. Obtener rango actual del miembro
            current_rank_id = RankService.get_user_current_rank(session, member_id)

            if not current_rank_id:
                print(f"⚠️  Usuario {member_id} no tiene rango asignado")
                return []

            rank = session.exec(
                sqlmodel.select(Ranks).where(Ranks.id == current_rank_id)
            ).first()

            if not rank:
                print(f"❌ Rango {current_rank_id} no encontrado")
                return []

            # 2. Obtener porcentajes según rango
            percentages = cls.UNILEVEL_BONUS_PERCENTAGES.get(rank.name, [])

            if not percentages:
                print(f"⚠️  No hay porcentajes definidos para rango {rank.name}")
                return []

            # 3. Obtener usuario para moneda
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()

            if not user:
                print(f"❌ Usuario {member_id} no encontrado")
                return []

            user_currency = ExchangeService.get_country_currency(user.country_cache)

            # 4. Calcular comisión por cada nivel
            commission_ids = []
            max_depth = len(percentages)

            for depth in range(1, max_depth + 1):
                # Para rangos Embajador (nivel 10+), calcular desde nivel 10 al infinito
                if depth == 10 and max_depth >= 10:
                    # Nivel infinito
                    infinity_percentage = percentages[9]  # Último porcentaje
                    vn_level = cls._sum_vn_from_depth_to_infinity(
                        session, member_id, period_id, start_depth=10
                    )
                    level_label = "10+"
                    percentage = infinity_percentage
                else:
                    # Nivel específico
                    percentage = percentages[depth - 1]
                    vn_level = cls._sum_vn_by_depth(session, member_id, period_id, depth)
                    level_label = str(depth)

                if vn_level <= 0:
                    continue

                # Calcular comisión
                commission_amount = vn_level * (percentage / 100)

                # Crear registro de comisión
                commission = Commissions(
                    member_id=member_id,
                    bonus_type=BonusType.BONO_UNINIVEL.value,
                    source_member_id=None,
                    source_order_id=None,
                    period_id=period_id,
                    level_depth=depth if depth < 10 else 10,
                    amount_vn=vn_level,
                    currency_origin=user_currency,
                    amount_converted=commission_amount,
                    currency_destination=user_currency,
                    exchange_rate=1.0,
                    calculated_at=datetime.now(timezone.utc),
                    paid_at=None,
                    notes=f"Bono Uninivel {percentage}% - Nivel {level_label} - VN: {vn_level:.2f}"
                )

                session.add(commission)
                session.flush()
                commission_ids.append(commission.id)

                print(f"✅ Comisión Uninivel creada: ${commission_amount:.2f} para member_id={member_id} nivel {level_label}")

                # Si procesamos nivel 10+, no continuar (ya se procesó infinito)
                if depth == 10 and max_depth >= 10:
                    break

            return commission_ids

        except Exception as e:
            print(f"❌ Error calculando Bono Uninivel para usuario {member_id}: {e}")
            return []

    @classmethod
    def _sum_vn_by_depth(cls, session, member_id: int, period_id: int, depth: int) -> float:
        """
        Suma el VN de todas las órdenes de productos (NO kits) de un nivel específico.
        Principio KISS: Query directo y eficiente.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro (ancestor)
            period_id: ID del período
            depth: Profundidad del nivel (1=directo, 2=segundo nivel, etc.)

        Returns:
            Total de VN del nivel
        """
        try:
            # Subquery para obtener descendientes del nivel específico
            descendants_subquery = (
                sqlmodel.select(UserTreePath.descendant_id)
                .where(
                    (UserTreePath.ancestor_id == member_id) &
                    (UserTreePath.depth == depth)
                )
                .subquery()
            )

            # Query principal: sumar VN de órdenes confirmadas de productos (NO kits)
            result = session.exec(
                sqlmodel.select(sqlmodel.func.sum(OrderItems.line_vn))
                .join(Orders, OrderItems.order_id == Orders.id)
                .join(Products, OrderItems.product_id == Products.id)
                .where(
                    (Orders.member_id.in_(sqlmodel.select(descendants_subquery))) &
                    (Orders.period_id == period_id) &
                    (Orders.status == OrderStatus.PAYMENT_CONFIRMED.value) &
                    (Products.type != "kit")  # Excluir kits
                )
            ).first()

            return float(result) if result else 0.0

        except Exception as e:
            print(f"❌ Error sumando VN nivel {depth}: {e}")
            return 0.0

    @classmethod
    def _sum_vn_from_depth_to_infinity(cls, session, member_id: int, period_id: int, start_depth: int) -> float:
        """
        Suma el VN desde un nivel hasta el infinito (para rangos Embajador).
        Principio DRY: Similar a _sum_vn_by_depth pero sin límite superior.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro (ancestor)
            period_id: ID del período
            start_depth: Profundidad inicial (típicamente 10)

        Returns:
            Total de VN desde start_depth hasta infinito
        """
        try:
            # Subquery para obtener todos los descendientes desde start_depth
            descendants_subquery = (
                sqlmodel.select(UserTreePath.descendant_id)
                .where(
                    (UserTreePath.ancestor_id == member_id) &
                    (UserTreePath.depth >= start_depth)
                )
                .subquery()
            )

            # Query principal: sumar VN de órdenes confirmadas de productos (NO kits)
            result = session.exec(
                sqlmodel.select(sqlmodel.func.sum(OrderItems.line_vn))
                .join(Orders, OrderItems.order_id == Orders.id)
                .join(Products, OrderItems.product_id == Products.id)
                .where(
                    (Orders.member_id.in_(sqlmodel.select(descendants_subquery))) &
                    (Orders.period_id == period_id) &
                    (Orders.status == OrderStatus.PAYMENT_CONFIRMED.value) &
                    (Products.type != "kit")  # Excluir kits
                )
            ).first()

            return float(result) if result else 0.0

        except Exception as e:
            print(f"❌ Error sumando VN desde nivel {start_depth}: {e}")
            return 0.0

    @classmethod
    def calculate_matching_bonus(cls, session, member_id: int, period_id: int) -> List[int]:
        """
        Calcula el Bono Matching (Bono de Igualación) para Embajadores.
        Reglas:
        - Solo elegible para rangos Embajador (Transformador+)
        - Se calcula sobre comisiones Uninivel de miembros Embajador en el equipo
        - Porcentajes: 30%/20%/10%/5% según rango y profundidad

        Principio KISS: Lógica clara nivel por nivel.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro Embajador
            period_id: ID del período mensual

        Returns:
            Lista de IDs de comisiones creadas
        """
        try:
            # 1. Obtener rango actual del miembro
            current_rank_id = RankService.get_user_current_rank(session, member_id)

            if not current_rank_id:
                print(f"⚠️  Usuario {member_id} no tiene rango asignado")
                return []

            rank = session.exec(
                sqlmodel.select(Ranks).where(Ranks.id == current_rank_id)
            ).first()

            if not rank:
                print(f"❌ Rango {current_rank_id} no encontrado")
                return []

            # 2. Verificar que sea rango Embajador
            if rank.name not in cls.AMBASSADOR_RANKS:
                print(f"⚠️  Rango {rank.name} no es elegible para Matching Bonus")
                return []

            # 3. Obtener porcentajes según rango
            percentages = cls.MATCHING_BONUS_PERCENTAGES.get(rank.name, [])

            if not percentages:
                print(f"⚠️  No hay porcentajes Matching para rango {rank.name}")
                return []

            # 4. Obtener usuario para moneda
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()

            if not user:
                print(f"❌ Usuario {member_id} no encontrado")
                return []

            user_currency = ExchangeService.get_country_currency(user.country_cache)

            # 5. Obtener todos los descendientes (downline completo)
            downline = GenealogyService.get_downline(session, member_id)

            if not downline:
                print(f"⚠️  Usuario {member_id} no tiene downline")
                return []

            # 6. Calcular comisión por cada nivel de profundidad de Embajadores
            commission_ids = []
            max_depth = len(percentages)

            for depth in range(1, max_depth + 1):
                percentage = percentages[depth - 1]

                # Obtener miembros de este nivel específico
                level_members = GenealogyService.get_level_members(session, member_id, depth)

                for descendant in level_members:
                    # Verificar que el descendiente sea Embajador
                    descendant_rank_id = RankService.get_user_current_rank(session, descendant.member_id)

                    if not descendant_rank_id:
                        continue

                    descendant_rank = session.exec(
                        sqlmodel.select(Ranks).where(Ranks.id == descendant_rank_id)
                    ).first()

                    if not descendant_rank or descendant_rank.name not in cls.AMBASSADOR_RANKS:
                        continue

                    # Obtener comisiones Uninivel del descendiente en este período
                    uninivel_earned = session.exec(
                        sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                        .where(
                            (Commissions.member_id == descendant.member_id) &
                            (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value) &
                            (Commissions.period_id == period_id)
                        )
                    ).first()

                    if not uninivel_earned or uninivel_earned <= 0:
                        continue

                    # Calcular Matching Bonus
                    matching_amount = uninivel_earned * (percentage / 100)

                    # Crear registro de comisión
                    commission = Commissions(
                        member_id=member_id,
                        bonus_type=BonusType.BONO_MATCHING.value,
                        source_member_id=descendant.member_id,
                        source_order_id=None,
                        period_id=period_id,
                        level_depth=depth,
                        amount_vn=uninivel_earned,
                        currency_origin=user_currency,
                        amount_converted=matching_amount,
                        currency_destination=user_currency,
                        exchange_rate=1.0,
                        calculated_at=datetime.now(timezone.utc),
                        paid_at=None,
                        notes=f"Matching Bonus {percentage}% - Nivel {depth} - Embajador: {descendant.member_id} - Uninivel: {uninivel_earned:.2f}"
                    )

                    session.add(commission)
                    session.flush()
                    commission_ids.append(commission.id)

                    print(f"✅ Comisión Matching creada: ${matching_amount:.2f} para member_id={member_id} desde {descendant.member_id}")

            return commission_ids

        except Exception as e:
            print(f"❌ Error calculando Matching Bonus para usuario {member_id}: {e}")
            return []

    @classmethod
    def process_achievement_bonus(cls, session, member_id: int, new_rank_name: str) -> Optional[int]:
        """
        Procesa el Bono por Alcance cuando un miembro alcanza un nuevo rango.
        Reglas:
        - Se paga UNA SOLA VEZ por cada rango alcanzado
        - Rango Emprendedor: máximo 30 días desde inscripción
        - Montos fijos por país según rango

        Principio KISS: Validaciones claras y directas.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro que alcanzó el rango
            new_rank_name: Nombre del nuevo rango alcanzado

        Returns:
            ID de la comisión creada o None si no es elegible
        """
        try:
            # 1. Verificar que el rango tenga bono
            if new_rank_name not in cls.ACHIEVEMENT_BONUS_AMOUNTS:
                print(f"⚠️  Rango {new_rank_name} no tiene Bono por Alcance")
                return None

            # 2. Obtener usuario
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()

            if not user:
                print(f"❌ Usuario {member_id} no encontrado")
                return None

            # 3. Verificar que no haya cobrado este bono antes
            existing_bonus = session.exec(
                sqlmodel.select(Commissions)
                .where(
                    (Commissions.member_id == member_id) &
                    (Commissions.bonus_type == BonusType.BONO_ALCANCE.value) &
                    (Commissions.notes.contains(new_rank_name))
                )
            ).first()

            if existing_bonus:
                print(f"⚠️  Usuario {member_id} ya cobró Bono por Alcance de {new_rank_name}")
                return None

            # 4. Validación especial: Rango Emprendedor (máximo 30 días)
            if new_rank_name == "Emprendedor":
                from NNProtect_new_website.utils.timezone_mx import get_mexico_now
                days_since_registration = (get_mexico_now() - user.created_at).days

                if days_since_registration > 30:
                    print(f"⚠️  Usuario {member_id} excedió 30 días para Bono Emprendedor ({days_since_registration} días)")
                    return None

            # 5. Obtener monto según país
            user_currency = ExchangeService.get_country_currency(user.country_cache)
            amount = cls.ACHIEVEMENT_BONUS_AMOUNTS[new_rank_name].get(user_currency)

            if not amount:
                print(f"❌ No hay monto definido para {new_rank_name} en {user_currency}")
                return None

            # 6. Obtener período actual
            period = cls._get_current_period(session)

            # 7. Crear comisión
            commission = Commissions(
                member_id=member_id,
                bonus_type=BonusType.BONO_ALCANCE.value,
                source_member_id=None,
                source_order_id=None,
                period_id=period.id if period else None,
                level_depth=None,
                amount_vn=amount,
                currency_origin=user_currency,
                amount_converted=amount,
                currency_destination=user_currency,
                exchange_rate=1.0,
                calculated_at=datetime.now(timezone.utc),
                paid_at=None,
                notes=f"Bono por Alcance - Rango: {new_rank_name} (primera vez)"
            )

            session.add(commission)
            session.flush()

            print(f"✅ Bono por Alcance creado: ${amount} {user_currency} para member_id={member_id} - Rango: {new_rank_name}")
            return commission.id

        except Exception as e:
            print(f"❌ Error procesando Bono por Alcance: {e}")
            return None

    @classmethod
    def _get_current_period(cls, session) -> Optional[Periods]:
        """
        Obtiene el período actual activo.
        Principio DRY: Método reutilizable.
        """
        try:
            from NNProtect_new_website.utils.timezone_mx import get_mexico_now
            current_date = get_mexico_now()

            current_period = session.exec(
                sqlmodel.select(Periods)
                .where(
                    (Periods.starts_on <= current_date) &
                    (Periods.ends_on >= current_date)
                )
            ).first()

            return current_period

        except Exception as e:
            print(f"❌ Error obteniendo período actual: {e}")
            return None
