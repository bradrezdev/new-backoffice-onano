"""
Servicio POO para gestión automática de rangos de usuarios MLM.
Maneja asignación inicial y tracking de historial de rangos.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import reflex as rx
import sqlmodel
from typing import Optional
from datetime import datetime, timezone

from database.users import Users
from database.ranks import Ranks
from database.user_rank_history import UserRankHistory
from database.periods import Periods
from database.orders import Orders, OrderStatus
from database.usertreepaths import UserTreePath
from ..utils.timezone_mx import get_mexico_now


class RankService:
    """
    Servicio POO para manejo automático de rangos de usuarios.
    Principio POO: Encapsula toda la lógica de gestión de rangos.
    """
    
    DEFAULT_RANK_ID = 1  # "Sin rango" - primer rango por defecto
    
    @classmethod
    def assign_initial_rank(cls, session, member_id: int) -> bool:
        """
        Asigna rango inicial "Sin rango" (id=1) a usuario recién registrado.
        Principio KISS: Método simple para asignación inicial.
        """
        try:
            # Verificar que el usuario existe
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()
            
            if not user:
                print(f"❌ Usuario con member_id {member_id} no encontrado")
                return False
            
            # Verificar que no tenga ya un rango asignado
            existing_rank = session.exec(
                sqlmodel.select(UserRankHistory).where(
                    UserRankHistory.member_id == member_id
                )
            ).first()
            
            if existing_rank:
                print(f"⚠️  Usuario {member_id} ya tiene rango asignado")
                return False
            
            # Obtener período actual (si existe)
            current_period = cls._get_current_period(session)
            period_id = current_period.id if current_period else None

            if current_period:
                print(f"📅 Período actual encontrado: ID={current_period.id}, Nombre={current_period.name}")
            else:
                print(f"⚠️ No hay período actual activo, period_id será NULL")

            # Crear registro de rango inicial
            rank_history = UserRankHistory(
                member_id=member_id,
                rank_id=cls.DEFAULT_RANK_ID,
                achieved_on=datetime.now(timezone.utc),
                period_id=period_id
            )

            session.add(rank_history)
            session.flush()

            print(f"✅ Rango inicial asignado a usuario {member_id}: Sin rango (id={cls.DEFAULT_RANK_ID}), period_id={period_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error asignando rango inicial a usuario {member_id}: {e}")
            return False
    
    @classmethod
    def get_user_current_rank(cls, session, member_id: int) -> Optional[int]:
        """
        Obtiene el rango actual de un usuario.
        Principio YAGNI: Solo obtiene lo necesario.
        """
        try:
            # Obtener el último rango asignado al usuario
            latest_rank = session.exec(
                sqlmodel.select(UserRankHistory)
                .where(UserRankHistory.member_id == member_id)
                .order_by(sqlmodel.desc(UserRankHistory.achieved_on))
            ).first()
            
            return latest_rank.rank_id if latest_rank else None
            
        except Exception as e:
            print(f"❌ Error obteniendo rango actual de usuario {member_id}: {e}")
            return None
    
    @classmethod
    def get_user_highest_rank(cls, session, member_id: int) -> Optional[int]:
        """
        Obtiene el rango más alto que ha alcanzado un usuario.
        Principio POO: Método específico para obtener máximo rango.
        """
        try:
            # Obtener el rango más alto (mayor ID = mayor nivel)
            highest_rank = session.exec(
                sqlmodel.select(UserRankHistory)
                .where(UserRankHistory.member_id == member_id)
                .order_by(sqlmodel.desc(UserRankHistory.rank_id))
            ).first()
            
            return highest_rank.rank_id if highest_rank else None
            
        except Exception as e:
            print(f"❌ Error obteniendo rango más alto de usuario {member_id}: {e}")
            return None
    
    @classmethod
    def promote_user_rank(cls, session, member_id: int, new_rank_id: int) -> bool:
        """
        Promueve usuario a un nuevo rango (si es mayor al actual).
        Dispara Bonos por Alcance de TODOS los rangos intermedios no cobrados.
        
        MEJORA (Giovanni - QA Financial):
        Si el usuario salta de rango 2 (Sin rango) → rango 5 (Innovador),
        debe recibir bonos de:
        - Rango 3 (Emprendedor)
        - Rango 4 (Creativo o Visionario)
        - Rango 5 (Innovador)
        
        Arquitectura: Elena (Backend) + Adrian (Senior Dev) + Giovanni (QA)
        """
        try:
            # Verificar que el nuevo rango existe
            new_rank = session.exec(
                sqlmodel.select(Ranks).where(Ranks.id == new_rank_id)
            ).first()

            if not new_rank:
                print(f"❌ Rango con ID {new_rank_id} no existe")
                return False

            # Obtener rango actual
            current_rank_id = cls.get_user_current_rank(session, member_id)

            # Solo promover si el nuevo rango es mayor
            if current_rank_id and new_rank_id <= current_rank_id:
                print(f"⚠️  Usuario {member_id} ya tiene rango igual o mayor ({current_rank_id})")
                return False

            # Obtener período actual
            current_period = cls._get_current_period(session)
            period_id = current_period.id if current_period else None

            # Crear nuevo registro de rango
            rank_history = UserRankHistory(
                member_id=member_id,
                rank_id=new_rank_id,
                achieved_on=datetime.now(timezone.utc),
                period_id=period_id
            )

            session.add(rank_history)
            session.flush()

            print(f"✅ Usuario {member_id} promovido a rango {new_rank.name} (id={new_rank_id})")

            # =================================================================
            # DISPARAR BONOS POR ALCANCE DE TODOS LOS RANGOS INTERMEDIOS
            # =================================================================
            from .commission_service import CommissionService
            
            # Obtener todos los rangos entre el actual y el nuevo
            start_rank = current_rank_id if current_rank_id else 1
            intermediate_ranks = session.exec(
                sqlmodel.select(Ranks)
                .where(
                    (Ranks.id > start_rank) &
                    (Ranks.id <= new_rank_id)
                )
                .order_by(Ranks.id)
            ).all()
            
            bonuses_generated = 0
            total_bonus_amount = 0.0
            
            for rank in intermediate_ranks:
                # Intentar generar bono para este rango
                achievement_commission_id = CommissionService.process_achievement_bonus(
                    session, member_id, rank.name
                )
                
                if achievement_commission_id:
                    bonuses_generated += 1
                    print(f"   ✅ Bono por Alcance generado: {rank.name}")
                    
                    # Obtener monto del bono generado
                    from database.comissions import Commissions
                    commission = session.exec(
                        sqlmodel.select(Commissions).where(Commissions.id == achievement_commission_id)
                    ).first()
                    
                    if commission:
                        total_bonus_amount += commission.amount_converted
            
            if bonuses_generated > 0:
                print(f"🎉 Total bonos generados: {bonuses_generated} rangos = ${total_bonus_amount:,.2f}")
            else:
                print(f"⚠️  No se generaron bonos de alcance (ya fueron cobrados previamente)")

            return True

        except Exception as e:
            print(f"❌ Error promoviendo usuario {member_id} a rango {new_rank_id}: {e}")
            return False
    
    @classmethod
    def get_rank_progression_history(cls, session, member_id: int) -> list:
        """
        Obtiene historial completo de progresión de rangos del usuario.
        Principio YAGNI: Solo para reportes específicos.
        """
        try:
            # Query separado para evitar problemas de JOIN en SQLModel
            rank_history = session.exec(
                sqlmodel.select(UserRankHistory)
                .where(UserRankHistory.member_id == member_id)
                .order_by(sqlmodel.desc(UserRankHistory.achieved_on))
            ).all()
            
            # Obtener nombres de rangos por separado
            result = []
            for history in rank_history:
                rank = session.exec(
                    sqlmodel.select(Ranks).where(Ranks.id == history.rank_id)
                ).first()
                
                result.append({
                    "rank_id": history.rank_id,
                    "rank_name": rank.name if rank else "Desconocido",
                    "achieved_on": history.achieved_on,
                    "period_id": history.period_id
                })
            
            return result
            
        except Exception as e:
            print(f"❌ Error obteniendo historial de rangos de usuario {member_id}: {e}")
            return []
    
    @classmethod
    def get_pv(cls, session, member_id: int, period_id: Optional[int] = None) -> int:
        """
        Calcula Puntos de Volumen Personal (PV) de compras personales.
        Principio KISS: Solo compras confirmadas del usuario.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro
            period_id: ID del período (opcional, si None = acumulado total)

        Returns:
            Total de PV del usuario
        """
        try:
            query = sqlmodel.select(sqlmodel.func.sum(Orders.total_pv)).where(
                (Orders.member_id == member_id) &
                (Orders.status == OrderStatus.PAYMENT_CONFIRMED.value)
            )

            if period_id:
                query = query.where(Orders.period_id == period_id)

            result = session.exec(query).first()
            return result if result else 0

        except Exception as e:
            print(f"❌ Error calculando PV de usuario {member_id}: {e}")
            return 0

    @classmethod
    def get_pvg(cls, session, member_id: int, period_id: Optional[int] = None) -> int:
        """
        Calcula Puntos de Volumen Grupal (PVG) en TIEMPO REAL.
        PVG = PV personal + PV de TODOS los descendientes.
        Principio DRY: Usa get_pv() para evitar duplicación.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro
            period_id: ID del período (opcional, si None = acumulado total)

        Returns:
            Total de PVG (personal + grupo)
        """
        try:
            # 1. Obtener PV personal
            personal_pv = cls.get_pv(session, member_id, period_id)

            # 2. Obtener todos los descendientes usando UserTreePath
            descendants = session.exec(
                sqlmodel.select(UserTreePath.descendant_id)
                .where(
                    (UserTreePath.ancestor_id == member_id) &
                    (UserTreePath.depth > 0)  # Excluir self-reference
                )
            ).all()

            # 3. Calcular PV de cada descendiente
            group_pv = 0
            for descendant_id in descendants:
                group_pv += cls.get_pv(session, descendant_id, period_id)

            return personal_pv + group_pv

        except Exception as e:
            print(f"❌ Error calculando PVG de usuario {member_id}: {e}")
            return 0

    @classmethod
    def calculate_rank(cls, session, member_id: int, period_id: Optional[int] = None) -> Optional[int]:
        """
        Calcula el rango que corresponde al usuario según PV y PVG.
        Reglas:
        - Mínimo 1,465 PV personal requerido
        - Rango determinado por PVG acumulado

        Principio KISS: Lógica directa de umbrales.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro
            period_id: ID del período (opcional)

        Returns:
            rank_id del rango alcanzado o None si no cumple requisitos
        """
        try:
            # Verificar PV mínimo personal
            pv = cls.get_pv(session, member_id, period_id)
            if pv < 1465:
                return cls.DEFAULT_RANK_ID  # "Sin rango"

            # Calcular PVG
            pvg = cls.get_pvg(session, member_id, period_id)

            # Obtener todos los rangos ordenados por PVG requerido (descendente)
            ranks = session.exec(
                sqlmodel.select(Ranks)
                .where(Ranks.pvg_required > 0)
                .order_by(sqlmodel.desc(Ranks.pvg_required))
            ).all()

            # Encontrar el rango más alto que cumple el requisito
            for rank in ranks:
                if pvg >= rank.pvg_required:
                    return rank.id

            # Si tiene PV suficiente pero no cumple ningún umbral de PVG
            return cls.DEFAULT_RANK_ID

        except Exception as e:
            print(f"❌ Error calculando rango de usuario {member_id}: {e}")
            return None
    
    @classmethod
    def calculate_rank_from_cache(cls, session, member_id: int) -> Optional[int]:
        """
        Calcula el rango usando pv_cache y pvg_cache (más eficiente).
        Usado cuando se actualizan los caches en tiempo real.
        
        Args:
            session: Sesión de base de datos
            member_id: ID del miembro
        
        Returns:
            rank_id del rango alcanzado o None si no cumple requisitos
        """
        try:
            # Obtener usuario con sus caches
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()
            
            if not user:
                print(f"❌ Usuario {member_id} no encontrado")
                return None
            
            # Verificar PV mínimo personal
            if user.pv_cache < 1465:
                return cls.DEFAULT_RANK_ID  # "Sin rango"
            
            # Usar pvg_cache para determinar rango
            pvg = user.pvg_cache
            
            # Obtener todos los rangos ordenados por PVG requerido (descendente)
            ranks = session.exec(
                sqlmodel.select(Ranks)
                .where(Ranks.pvg_required > 0)
                .order_by(sqlmodel.desc(Ranks.pvg_required))
            ).all()
            
            # Encontrar el rango más alto que cumple el requisito
            for rank in ranks:
                if pvg >= rank.pvg_required:
                    return rank.id
            
            # Si tiene PV suficiente pero no cumple ningún umbral de PVG
            return cls.DEFAULT_RANK_ID
        
        except Exception as e:
            print(f"❌ Error calculando rango desde cache de usuario {member_id}: {e}")
            return None

    @classmethod
    def check_and_update_rank(cls, session, member_id: int, use_cache: bool = True) -> bool:
        """
        Verifica si el usuario califica para nuevo rango y lo actualiza.
        Principio POO: Encapsula lógica de detección y actualización.

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro
            use_cache: Si True, usa pv_cache/pvg_cache (más rápido); si False, recalcula desde órdenes

        Returns:
            True si hubo promoción, False si no
        """
        try:
            # Calcular rango que corresponde (usando cache o recalculando)
            if use_cache:
                calculated_rank_id = cls.calculate_rank_from_cache(session, member_id)
            else:
                current_period = cls._get_current_period(session)
                period_id = current_period.id if current_period else None
                calculated_rank_id = cls.calculate_rank(session, member_id, period_id)

            if not calculated_rank_id:
                return False

            # Obtener rango actual
            current_rank_id = cls.get_user_current_rank(session, member_id)

            # Solo promover si el nuevo rango es mayor
            if not current_rank_id or calculated_rank_id > current_rank_id:
                return cls.promote_user_rank(session, member_id, calculated_rank_id)

            return False

        except Exception as e:
            print(f"❌ Error verificando rango de usuario {member_id}: {e}")
            return False

    @classmethod
    def _get_current_period(cls, session) -> Optional[Periods]:
        """
        Obtiene el período actual activo.
        Principio KISS: Método helper simple.
        """
        try:
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