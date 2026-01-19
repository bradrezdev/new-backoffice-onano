"""
Servicio POO para gestión de puntos de lealtad.
Maneja acumulación de 25 puntos por compra en día 1-7, reset automático y canje de recompensas.

Principios aplicados: KISS, DRY, YAGNI, POO
CRÍTICO: Si un mes no compra en día 1-7 → RESETEO A 0
"""

import sqlmodel
from typing import Optional, Dict
from datetime import datetime, timezone

from database.loyalty_points import (
    LoyaltyPoints, LoyaltyPointsHistory, LoyaltyRewards,
    LoyaltyStatus, LoyaltyEventType, RewardType, RewardStatus
)


class LoyaltyService:
    """
    Servicio POO para gestión de puntos de lealtad.
    Principio POO: Encapsula lógica de lealtad con regla crítica de ventana 1-7.
    """

    POINTS_PER_MONTH = 25
    TARGET_POINTS = 100  # 4 meses consecutivos
    VALID_PURCHASE_DAYS = range(1, 8)  # Días 1-7 del mes

    @classmethod
    def get_or_create_loyalty_record(cls, session, member_id: int) -> Optional[LoyaltyPoints]:
        """
        Obtiene o crea el registro de lealtad de un usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario

        Returns:
            Registro de lealtad o None si falla
        """
        try:
            # Buscar registro existente
            loyalty = session.exec(
                sqlmodel.select(LoyaltyPoints).where(LoyaltyPoints.member_id == member_id)
            ).first()

            if loyalty:
                return loyalty

            # Crear nuevo registro
            loyalty = LoyaltyPoints(
                member_id=member_id,
                current_points=0,
                consecutive_months=0,
                last_valid_purchase_date=None,
                status=LoyaltyStatus.ACUMULANDO.value
            )

            session.add(loyalty)
            session.flush()

            return loyalty

        except Exception as e:
            print(f"❌ Error obteniendo/creando registro de lealtad para usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def is_valid_purchase_day(cls, purchase_date: datetime) -> bool:
        """
        Verifica si la fecha de compra está en la ventana válida (día 1-7).

        Args:
            purchase_date: Fecha de compra (UTC)

        Returns:
            True si está en día 1-7, False en caso contrario
        """
        purchase_day = purchase_date.day
        return purchase_day in cls.VALID_PURCHASE_DAYS

    @classmethod
    def process_purchase(
        cls,
        session,
        member_id: int,
        order_id: int,
        period_id: int,
        purchase_date: datetime
    ) -> bool:
        """
        Procesa una compra para el programa de lealtad.
        CRÍTICO: Solo compras entre día 1-7 del mes cuentan.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            order_id: ID de la orden
            period_id: ID del período
            purchase_date: Fecha de compra (UTC)

        Returns:
            True si se procesó exitosamente, False si falló
        """
        try:
            # Verificar que la compra sea en día 1-7
            if not cls.is_valid_purchase_day(purchase_date):
                purchase_day = purchase_date.day
                print(f"⚠️  Compra en día {purchase_day} no válida para lealtad (debe ser día 1-7)")
                return False

            # Obtener o crear registro de lealtad
            loyalty = cls.get_or_create_loyalty_record(session, member_id)
            if not loyalty:
                return False

            # Verificar si ya ganó puntos este mes
            if loyalty.last_valid_purchase_date:
                last_purchase_month = loyalty.last_valid_purchase_date.month
                current_month = purchase_date.month

                if last_purchase_month == current_month:
                    print(f"⚠️  Usuario {member_id} ya ganó puntos este mes")
                    return False

            # Añadir 25 puntos
            points_before = loyalty.current_points
            loyalty.add_points(purchase_date)
            points_after = loyalty.current_points

            # Crear historial
            history = LoyaltyPointsHistory(
                member_id=member_id,
                period_id=period_id,
                event_type=LoyaltyEventType.EARNED.value,
                points_before=points_before,
                points_after=points_after,
                points_change=cls.POINTS_PER_MONTH,
                order_id=order_id,
                purchase_day=purchase_date.day,
                description=f"Ganó {cls.POINTS_PER_MONTH} puntos por compra en día {purchase_date.day}"
            )

            session.add(history)
            session.flush()

            print(f"✅ Usuario {member_id} ganó {cls.POINTS_PER_MONTH} puntos de lealtad (total: {points_after})")

            # Si alcanzó 100 puntos, crear recompensa
            if points_after >= cls.TARGET_POINTS and loyalty.status == LoyaltyStatus.CALIFICADO.value:
                cls._create_reward(session, member_id)

            return True

        except Exception as e:
            print(f"❌ Error procesando compra de lealtad para usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def _create_reward(cls, session, member_id: int) -> Optional[int]:
        """
        Crea una recompensa pendiente para el usuario que alcanzó 100 puntos.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario

        Returns:
            ID de recompensa creada o None si falla
        """
        try:
            # Por defecto, asignar el primer tipo de recompensa
            # En producción, esto podría ser seleccionado por el usuario
            reward_type = RewardType.PAQUETE_5_SUPLEMENTOS.value

            reward = LoyaltyRewards(
                member_id=member_id,
                reward_type=reward_type,
                earned_at=datetime.now(timezone.utc),
                status=RewardStatus.PENDING.value
            )

            session.add(reward)
            session.flush()

            print(f"✅ Recompensa de lealtad creada para usuario {member_id} (ID: {reward.id})")
            return reward.id

        except Exception as e:
            print(f"❌ Error creando recompensa para usuario {member_id}: {e}")
            return None

    @classmethod
    def reset_points(
        cls,
        session,
        member_id: int,
        period_id: int,
        reason: str
    ) -> bool:
        """
        Reinicia los puntos de un usuario a 0.
        Usado cuando no compra en la ventana 1-7 de un mes.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            period_id: ID del período
            reason: Razón del reset

        Returns:
            True si se reseteo exitosamente, False si falló
        """
        try:
            loyalty = session.exec(
                sqlmodel.select(LoyaltyPoints).where(LoyaltyPoints.member_id == member_id)
            ).first()

            if not loyalty:
                print(f"⚠️  Usuario {member_id} no tiene registro de lealtad")
                return False

            if loyalty.current_points == 0:
                print(f"⚠️  Usuario {member_id} ya tiene 0 puntos")
                return True

            # Guardar puntos antes del reset
            points_before = loyalty.current_points

            # Resetear puntos
            loyalty.reset_points()

            # Crear historial
            history = LoyaltyPointsHistory(
                member_id=member_id,
                period_id=period_id,
                event_type=LoyaltyEventType.RESET.value,
                points_before=points_before,
                points_after=0,
                points_change=-points_before,
                description=reason
            )

            session.add(history)
            session.flush()

            print(f"✅ Puntos de lealtad de usuario {member_id} reseteados a 0 (tenía {points_before})")
            return True

        except Exception as e:
            print(f"❌ Error reseteando puntos de usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def redeem_reward(
        cls,
        session,
        member_id: int,
        reward_id: int,
        delivery_order_id: int,
        period_id: int
    ) -> bool:
        """
        Canjea una recompensa de lealtad.
        Marca como entregada y resetea puntos del usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            reward_id: ID de la recompensa
            delivery_order_id: ID de la orden de entrega
            period_id: ID del período

        Returns:
            True si se canjeó exitosamente, False si falló
        """
        try:
            # Obtener recompensa
            reward = session.get(LoyaltyRewards, reward_id)
            if not reward:
                print(f"❌ Recompensa {reward_id} no existe")
                return False

            if reward.member_id != member_id:
                print(f"❌ Recompensa {reward_id} no pertenece al usuario {member_id}")
                return False

            if reward.status != RewardStatus.PENDING.value:
                print(f"⚠️  Recompensa {reward_id} ya fue procesada (status: {reward.status})")
                return False

            # Marcar recompensa como entregada
            reward.mark_as_delivered(delivery_order_id)

            # Obtener registro de lealtad
            loyalty = session.exec(
                sqlmodel.select(LoyaltyPoints).where(LoyaltyPoints.member_id == member_id)
            ).first()

            if loyalty:
                points_before = loyalty.current_points

                # Canjear recompensa (resetea a 0)
                loyalty.redeem_reward()

                # Crear historial
                history = LoyaltyPointsHistory(
                    member_id=member_id,
                    period_id=period_id,
                    event_type=LoyaltyEventType.REDEEMED.value,
                    points_before=points_before,
                    points_after=0,
                    points_change=-points_before,
                    description=f"Canjeó recompensa {reward.reward_type}"
                )

                session.add(history)

            session.flush()

            print(f"✅ Recompensa {reward_id} canjeada exitosamente para usuario {member_id}")
            return True

        except Exception as e:
            print(f"❌ Error canjeando recompensa {reward_id} para usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def check_and_reset_inactive_users(cls, session, period_id: int) -> int:
        """
        Revisa todos los usuarios con puntos y resetea los que no compraron en día 1-7.
        Job automático que se ejecuta el día 8 de cada mes.

        Args:
            session: Sesión de base de datos
            period_id: ID del período actual

        Returns:
            Cantidad de usuarios reseteados
        """
        try:
            # Obtener el período anterior (mes pasado)
            # En producción, calcular correctamente el período anterior
            previous_month = datetime.now(timezone.utc).replace(day=1)

            # Obtener todos los usuarios con puntos > 0
            users_with_points = session.exec(
                sqlmodel.select(LoyaltyPoints)
                .where(LoyaltyPoints.current_points > 0)
            ).all()

            reset_count = 0

            for loyalty in users_with_points:
                # Verificar si hubo compra válida en el mes anterior
                if loyalty.last_valid_purchase_date:
                    last_purchase_month = loyalty.last_valid_purchase_date.month
                    last_purchase_year = loyalty.last_valid_purchase_date.year
                    previous_month_num = previous_month.month
                    previous_year = previous_month.year

                    # Si la última compra NO fue en el mes anterior, resetear
                    if last_purchase_month != previous_month_num or last_purchase_year != previous_year:
                        success = cls.reset_points(
                            session=session,
                            member_id=loyalty.member_id,
                            period_id=period_id,
                            reason=f"Reinicio automático por falta de compra en ventana 1-7 del mes anterior"
                        )
                        if success:
                            reset_count += 1
                else:
                    # Si nunca ha comprado, resetear
                    success = cls.reset_points(
                        session=session,
                        member_id=loyalty.member_id,
                        period_id=period_id,
                        reason="Reinicio automático por falta de compra"
                    )
                    if success:
                        reset_count += 1

            session.commit()

            print(f"✅ Job de reset de lealtad completado: {reset_count} usuarios reseteados")
            return reset_count

        except Exception as e:
            print(f"❌ Error en job de reset de lealtad: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return 0

    @classmethod
    def get_user_loyalty_summary(cls, session, member_id: int) -> Optional[Dict]:
        """
        Obtiene el resumen de puntos de lealtad de un usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario

        Returns:
            Diccionario con resumen de lealtad o None
        """
        try:
            loyalty = session.exec(
                sqlmodel.select(LoyaltyPoints).where(LoyaltyPoints.member_id == member_id)
            ).first()

            if not loyalty:
                return {
                    "member_id": member_id,
                    "current_points": 0,
                    "consecutive_months": 0,
                    "target_points": cls.TARGET_POINTS,
                    "status": LoyaltyStatus.ACUMULANDO.value,
                    "last_valid_purchase_date": None
                }

            return {
                "member_id": loyalty.member_id,
                "current_points": loyalty.current_points,
                "consecutive_months": loyalty.consecutive_months,
                "target_points": cls.TARGET_POINTS,
                "status": loyalty.status,
                "last_valid_purchase_date": loyalty.last_valid_purchase_date
            }

        except Exception as e:
            print(f"❌ Error obteniendo resumen de lealtad de usuario {member_id}: {e}")
            return None
