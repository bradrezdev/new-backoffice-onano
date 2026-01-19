"""
Servicio para actualizar PV de usuarios cuando se confirma una orden.
Actualiza PV del comprador y dispara actualización de rangos.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import sqlmodel
from typing import Optional

from database.users import Users
from database.orders import Orders
from .rank_service import RankService
from .genealogy_service import GenealogyService


class PVUpdateService:
    """
    Servicio POO para actualizar PV de usuarios.
    Principio POO: Encapsula lógica de actualización de PV y rangos.
    """

    @classmethod
    def process_order_pv_update(cls, session, order_id: int) -> bool:
        """
        Procesa actualización de PV y PVG cuando se confirma el pago de una orden.

        Flujo:
        1. Obtener orden y validar
        2. Actualizar PV del comprador (pv_cache)
        3. Actualizar PVG de todos los ancestros
        4. Verificar y actualizar rango del comprador

        Principio KISS: Proceso lineal y directo.

        Args:
            session: Sesión de base de datos
            order_id: ID de la orden confirmada

        Returns:
            True si se procesó correctamente, False si falló
        """
        try:
            # 1. Obtener orden
            order = session.exec(
                sqlmodel.select(Orders).where(Orders.id == order_id)
            ).first()

            if not order:
                print(f"❌ Orden {order_id} no encontrada")
                return False

            if not order.payment_confirmed_at:
                print(f"⚠️  Orden {order_id} no tiene pago confirmado")
                return False

            print(f"📊 Procesando actualización PV/PVG para orden {order_id}...")

            # 2. Actualizar PV del comprador
            buyer = session.exec(
                sqlmodel.select(Users).where(Users.member_id == order.member_id)
            ).first()

            if not buyer:
                print(f"❌ Comprador {order.member_id} no encontrado")
                return False

            # Sumar PV de la orden al cache
            pv_anterior = buyer.pv_cache
            buyer.pv_cache += order.total_pv

            # Actualizar PVG del comprador (PVG incluye su propio PV)
            pvg_anterior = buyer.pvg_cache
            buyer.pvg_cache += order.total_pv

            session.add(buyer)
            session.flush()

            print(f"✅ PV actualizado para member_id={buyer.member_id}: {pv_anterior} -> {buyer.pv_cache} (+{order.total_pv})")
            print(f"✅ PVG actualizado para member_id={buyer.member_id}: {pvg_anterior} -> {buyer.pvg_cache} (+{order.total_pv})")

            # 3. Actualizar PVG de todos los ancestros (excluyendo el comprador)
            cls._update_pvg_for_ancestors(session, buyer.member_id, order.total_pv)

            # 3b. Actualizar tabla unilevel_report para el comprador y ancestros
            print("📊 Actualizando unilevel_report...")
            from .mlm_user_manager import MLMUserManager
            MLMUserManager.update_unilevel_report_for_order(order.member_id, order.period_id)

            # 4. Verificar y actualizar rango del comprador
            rank_updated = RankService.check_and_update_rank(session, buyer.member_id)

            if rank_updated:
                print(f"🎖️  Rango actualizado para member_id={buyer.member_id}")

            # ⚠️ NO hacer commit aquí - el PaymentService hará el commit final
            # Esto garantiza atomicidad: todo o nada
            session.flush()  # Solo flush para verificar constraints
            return True

        except Exception as e:
            session.rollback()
            print(f"❌ Error procesando actualización PV: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def _update_pvg_for_ancestors(cls, session, member_id: int, pv_amount: int) -> None:
        """
        Actualiza PVG_cache de todos los ancestros cuando se añade PV.
        Excluye al propio usuario (ya se actualizó su PVG en el paso anterior).

        Principio DRY: Método reutilizable para actualizar PVG.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro que generó el PV
            pv_amount: Cantidad de PV a sumar
        """
        try:
            # Obtener todos los ancestros (incluyendo self)
            all_ancestors = GenealogyService.get_all_ancestors(session, member_id)

            # Excluir al propio usuario (depth > 0)
            ancestors = [ancestor_id for ancestor_id in all_ancestors if ancestor_id != member_id]

            for ancestor_id in ancestors:
                ancestor = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == ancestor_id)
                ).first()

                if ancestor:
                    pvg_anterior = ancestor.pvg_cache
                    ancestor.pvg_cache += pv_amount
                    session.add(ancestor)
                    print(f"📈 PVG actualizado para ancestor member_id={ancestor_id}: {pvg_anterior} -> {ancestor.pvg_cache} (+{pv_amount})")

            session.flush()

        except Exception as e:
            print(f"❌ Error actualizando PVG de ancestros: {e}")
            raise
