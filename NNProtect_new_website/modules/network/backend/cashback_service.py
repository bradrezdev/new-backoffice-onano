"""
Servicio POO para gestión de cashback.
Maneja generación automática al alcanzar 2,930 PV y aplicación de descuento 70%.

Principios aplicados: KISS, DRY, YAGNI, POO
CRÍTICO: Cashback es 70% de descuento sobre precio público, válido hasta fin de mes
"""

import sqlmodel
from typing import Optional, Dict, List
from datetime import datetime, timezone
from calendar import monthrange

from database.cashback import Cashback, CashbackUsage, CashbackStatus
from database.orders import Orders
from database.order_items import OrderItems


class CashbackService:
    """
    Servicio POO para gestión de cashback.
    Principio POO: Encapsula lógica de cashback con requisito de 2,930 PV.
    """

    REQUIRED_PV = 2930
    DISCOUNT_PERCENTAGE = 0.70  # 70% de descuento

    @classmethod
    def generate_cashback(
        cls,
        session,
        member_id: int,
        order_id: int,
        period_id: int,
        pv_accumulated: int,
        total_public_price: float,
        currency: str
    ) -> Optional[int]:
        """
        Genera un cashback al alcanzar 2,930 PV en una orden.
        Principio KISS: Validación simple + creación de cashback.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            order_id: ID de la orden que generó el cashback
            period_id: ID del período
            pv_accumulated: PV acumulado en la orden
            total_public_price: Precio público total de productos
            currency: Moneda del usuario

        Returns:
            ID del cashback creado o None si falla
        """
        try:
            # Validar que alcanzó el PV requerido
            if pv_accumulated < cls.REQUIRED_PV:
                print(f"⚠️  Usuario {member_id} no alcanzó PV requerido: {pv_accumulated}/{cls.REQUIRED_PV}")
                return None

            # Calcular descuento (70% del precio público)
            discount_amount = total_public_price * cls.DISCOUNT_PERCENTAGE

            # Calcular fecha de expiración (fin del mes)
            now = datetime.now(timezone.utc)
            last_day = monthrange(now.year, now.month)[1]
            expires_at = now.replace(day=last_day, hour=23, minute=59, second=59)

            # Crear cashback
            cashback = Cashback(
                member_id=member_id,
                period_id=period_id,
                generated_by_order_id=order_id,
                pv_accumulated=pv_accumulated,
                discount_amount=discount_amount,
                currency=currency,
                applied_to_order_id=None,
                issued_at=now,
                expires_at=expires_at,
                status=CashbackStatus.AVAILABLE.value
            )

            session.add(cashback)
            session.flush()

            print(f"✅ Cashback generado para usuario {member_id}: {discount_amount} {currency} (ID: {cashback.id})")
            return cashback.id

        except Exception as e:
            print(f"❌ Error generando cashback para usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def get_available_cashback(cls, session, member_id: int) -> Optional[Cashback]:
        """
        Obtiene el cashback disponible (no expirado ni usado) de un usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario

        Returns:
            Cashback disponible o None
        """
        try:
            now = datetime.now(timezone.utc)

            cashback = session.exec(
                sqlmodel.select(Cashback)
                .where(
                    (Cashback.member_id == member_id) &
                    (Cashback.status == CashbackStatus.AVAILABLE.value) &
                    (Cashback.expires_at >= now)
                )
                .order_by(sqlmodel.desc(Cashback.issued_at))
            ).first()

            return cashback

        except Exception as e:
            print(f"❌ Error obteniendo cashback disponible para usuario {member_id}: {e}")
            return None

    @classmethod
    def apply_cashback_to_order(
        cls,
        session,
        cashback_id: int,
        order_id: int,
        order_items: List[Dict]
    ) -> bool:
        """
        Aplica un cashback a una orden específica.
        Principio: Atomicidad - todo o nada.

        Args:
            session: Sesión de base de datos
            cashback_id: ID del cashback
            order_id: ID de la orden
            order_items: Lista de items con {"order_item_id", "product_id", "quantity", "original_price"}

        Returns:
            True si se aplicó exitosamente, False si falló
        """
        try:
            # Obtener cashback
            cashback = session.get(Cashback, cashback_id)
            if not cashback:
                print(f"❌ Cashback {cashback_id} no existe")
                return False

            # Verificar que está disponible y no expiró
            if not cashback.is_valid():
                print(f"❌ Cashback {cashback_id} no está disponible o expiró")
                return False

            # Obtener orden
            order = session.get(Orders, order_id)
            if not order:
                print(f"❌ Orden {order_id} no existe")
                return False

            if order.member_id != cashback.member_id:
                print(f"❌ Orden {order_id} no pertenece al mismo usuario del cashback")
                return False

            # Aplicar descuento a cada item
            total_discount_applied = 0.0

            for item_data in order_items:
                original_price = item_data["original_price"]
                quantity = item_data["quantity"]
                discount_per_unit = original_price * cls.DISCOUNT_PERCENTAGE
                final_price_per_unit = original_price - discount_per_unit

                # Crear registro de uso de cashback
                usage = CashbackUsage(
                    cashback_id=cashback_id,
                    order_id=order_id,
                    order_item_id=item_data["order_item_id"],
                    product_id=item_data["product_id"],
                    quantity=quantity,
                    original_price=original_price,
                    discount_applied=discount_per_unit * quantity,
                    final_price=final_price_per_unit * quantity
                )

                session.add(usage)
                total_discount_applied += discount_per_unit * quantity

            # Actualizar orden con descuento
            order.discount = total_discount_applied
            order.total = order.subtotal + order.shipping_cost + order.tax - order.discount

            # Marcar cashback como usado
            cashback.mark_as_used(order_id)

            session.flush()

            print(f"✅ Cashback {cashback_id} aplicado a orden {order_id}: -{total_discount_applied} {cashback.currency}")
            return True

        except Exception as e:
            print(f"❌ Error aplicando cashback {cashback_id} a orden {order_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def calculate_discount_for_cart(
        cls,
        cart_items: List[Dict],
        cashback: Optional[Cashback]
    ) -> Dict:
        """
        Calcula el descuento aplicable a un carrito con cashback.
        Principio KISS: Cálculo simple de descuento sin modificar BD.

        Args:
            cart_items: Lista de items con {"product_id", "quantity", "original_price"}
            cashback: Cashback disponible (o None)

        Returns:
            Diccionario con resumen de descuento
        """
        if not cashback:
            return {
                "has_cashback": False,
                "discount_amount": 0.0,
                "total_before_discount": 0.0,
                "total_after_discount": 0.0,
                "items": []
            }

        total_before = 0.0
        total_discount = 0.0
        discounted_items = []

        for item in cart_items:
            original_price = item["original_price"]
            quantity = item["quantity"]
            discount_per_unit = original_price * cls.DISCOUNT_PERCENTAGE
            final_price_per_unit = original_price - discount_per_unit

            item_total_before = original_price * quantity
            item_total_discount = discount_per_unit * quantity
            item_total_after = final_price_per_unit * quantity

            total_before += item_total_before
            total_discount += item_total_discount

            discounted_items.append({
                "product_id": item["product_id"],
                "quantity": quantity,
                "original_price": original_price,
                "discount_per_unit": discount_per_unit,
                "final_price_per_unit": final_price_per_unit,
                "total_before": item_total_before,
                "total_discount": item_total_discount,
                "total_after": item_total_after
            })

        return {
            "has_cashback": True,
            "cashback_id": cashback.id,
            "discount_percentage": int(cls.DISCOUNT_PERCENTAGE * 100),
            "discount_amount": total_discount,
            "total_before_discount": total_before,
            "total_after_discount": total_before - total_discount,
            "currency": cashback.currency,
            "expires_at": cashback.expires_at,
            "items": discounted_items
        }

    @classmethod
    def expire_old_cashbacks(cls, session) -> int:
        """
        Marca como expirados todos los cashbacks que pasaron su fecha de expiración.
        Job automático que se ejecuta diariamente.

        Args:
            session: Sesión de base de datos

        Returns:
            Cantidad de cashbacks expirados
        """
        try:
            now = datetime.now(timezone.utc)

            # Obtener cashbacks disponibles que expiraron
            expired_cashbacks = session.exec(
                sqlmodel.select(Cashback)
                .where(
                    (Cashback.status == CashbackStatus.AVAILABLE.value) &
                    (Cashback.expires_at < now)
                )
            ).all()

            expired_count = 0

            for cashback in expired_cashbacks:
                cashback.mark_as_expired()
                expired_count += 1

            session.commit()

            print(f"✅ Job de expiración de cashbacks completado: {expired_count} cashbacks expirados")
            return expired_count

        except Exception as e:
            print(f"❌ Error en job de expiración de cashbacks: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return 0

    @classmethod
    def check_order_qualifies_for_cashback(
        cls,
        session,
        member_id: int,
        order_id: int
    ) -> Dict:
        """
        Verifica si una orden califica para generar cashback.
        Retorna información de PV acumulado y si alcanza el requisito.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            order_id: ID de la orden

        Returns:
            Diccionario con información de calificación
        """
        try:
            # Obtener orden
            order = session.get(Orders, order_id)
            if not order:
                return {
                    "qualifies": False,
                    "reason": "Orden no existe"
                }

            # Verificar PV de la orden
            order_pv = order.total_pv

            qualifies = order_pv >= cls.REQUIRED_PV

            return {
                "qualifies": qualifies,
                "order_pv": order_pv,
                "required_pv": cls.REQUIRED_PV,
                "pv_remaining": max(0, cls.REQUIRED_PV - order_pv),
                "discount_percentage": int(cls.DISCOUNT_PERCENTAGE * 100),
                "currency": order.currency
            }

        except Exception as e:
            print(f"❌ Error verificando calificación de cashback para orden {order_id}: {e}")
            return {
                "qualifies": False,
                "reason": "Error en verificación"
            }

    @classmethod
    def get_user_cashback_history(
        cls,
        session,
        member_id: int,
        limit: int = 20
    ) -> List[Dict]:
        """
        Obtiene el historial de cashbacks de un usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            limit: Límite de resultados

        Returns:
            Lista de cashbacks
        """
        try:
            cashbacks = session.exec(
                sqlmodel.select(Cashback)
                .where(Cashback.member_id == member_id)
                .order_by(sqlmodel.desc(Cashback.issued_at))
                .limit(limit)
            ).all()

            history = []
            for cashback in cashbacks:
                history.append({
                    "id": cashback.id,
                    "discount_amount": cashback.discount_amount,
                    "currency": cashback.currency,
                    "pv_accumulated": cashback.pv_accumulated,
                    "status": cashback.status,
                    "issued_at": cashback.issued_at,
                    "expires_at": cashback.expires_at,
                    "generated_by_order_id": cashback.generated_by_order_id,
                    "applied_to_order_id": cashback.applied_to_order_id
                })

            return history

        except Exception as e:
            print(f"❌ Error obteniendo historial de cashbacks de usuario {member_id}: {e}")
            return []
