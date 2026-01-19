"""
Servicio de Genealogía MLM.
Maneja la estructura de red usando UserTreePath (Closure Table Pattern).
"""
import reflex as rx
from sqlmodel import select
from typing import List, Optional
from database.usertreepaths import UserTreePath
from database.users import Users


class GenealogyService:
    """
    Servicio para manejar la estructura de red (UserTreePath).
    Principio: Path Enumeration para queries eficientes sin recursión.
    """

    @staticmethod
    def add_member_to_tree(session, new_member_id: int, sponsor_id: int) -> bool:
        """
        Agrega un nuevo miembro al árbol genealógico.
        Crea TODOS los registros necesarios en UserTreePath.

        CRÍTICO: Se ejecuta en transacción atómica junto con registro del usuario.

        Args:
            session: Sesión de base de datos activa
            new_member_id: member_id del nuevo usuario
            sponsor_id: member_id del sponsor (puede ser None para primer usuario)

        Returns:
            bool: True si se agregó exitosamente

        Algoritmo:
            1. Insertar registro self (depth=0)
            2. Copiar TODAS las relaciones del sponsor incrementando depth
            3. Crear relación directa con sponsor (depth=1)
        """
        try:
            # 1. Crear relación self (depth=0)
            self_path = UserTreePath(
                ancestor_id=new_member_id,
                descendant_id=new_member_id,
                depth=0
            )
            session.add(self_path)

            # Si no tiene sponsor (primer usuario), terminar aquí
            if sponsor_id is None or sponsor_id == 0:
                return True

            # 2. Copiar TODAS las relaciones del sponsor + nueva relación
            # Equivalente SQL:
            # INSERT INTO usertreepaths (ancestor_id, descendant_id, depth)
            # SELECT ancestor_id, new_member_id, depth + 1
            # FROM usertreepaths
            # WHERE descendant_id = sponsor_id

            sponsor_paths = session.exec(
                select(UserTreePath).where(UserTreePath.descendant_id == sponsor_id)
            ).all()

            for path in sponsor_paths:
                new_path = UserTreePath(
                    ancestor_id=path.ancestor_id,
                    descendant_id=new_member_id,
                    depth=path.depth + 1
                )
                session.add(new_path)

            print(f"✅ Genealogía creada: member_id={new_member_id}, sponsor_id={sponsor_id}")
            return True

        except Exception as e:
            print(f"❌ Error agregando miembro al árbol: {e}")
            return False

    @staticmethod
    def get_upline(session, member_id: int, max_depth: Optional[int] = None) -> List[Users]:
        """
        Obtiene los patrocinadores ascendentes de un miembro.

        Args:
            session: Sesión de base de datos
            member_id: member_id del usuario
            max_depth: Profundidad máxima (None = todos los niveles)

        Returns:
            List[Users]: Lista de sponsors ordenados por cercanía (1=directo, 2=abuelo, etc.)

        Query optimizado:
            SELECT u.*
            FROM usertreepaths utp
            JOIN users u ON u.member_id = utp.ancestor_id
            WHERE utp.descendant_id = :member_id
              AND utp.depth > 0
            ORDER BY utp.depth ASC
        """
        try:
            query = (
                select(Users)
                .join(UserTreePath, Users.member_id == UserTreePath.ancestor_id)
                .where(
                    UserTreePath.descendant_id == member_id,
                    UserTreePath.depth > 0  # Excluir self
                )
                .order_by(UserTreePath.depth.asc())
            )

            if max_depth is not None:
                query = query.where(UserTreePath.depth <= max_depth)

            upline = session.exec(query).all()
            return list(upline)

        except Exception as e:
            print(f"❌ Error obteniendo upline: {e}")
            return []

    @staticmethod
    def get_downline(session, member_id: int, max_depth: Optional[int] = None) -> List[Users]:
        """
        Obtiene todos los descendientes de un miembro.

        Args:
            session: Sesión de base de datos
            member_id: member_id del usuario
            max_depth: Profundidad máxima (None = todos los niveles)

        Returns:
            List[Users]: Lista de descendientes ordenados por cercanía

        Query optimizado:
            SELECT u.*
            FROM usertreepaths utp
            JOIN users u ON u.member_id = utp.descendant_id
            WHERE utp.ancestor_id = :member_id
              AND utp.depth > 0
            ORDER BY utp.depth ASC
        """
        try:
            query = (
                select(Users)
                .join(UserTreePath, Users.member_id == UserTreePath.descendant_id)
                .where(
                    UserTreePath.ancestor_id == member_id,
                    UserTreePath.depth > 0  # Excluir self
                )
                .order_by(UserTreePath.depth.asc())
            )

            if max_depth is not None:
                query = query.where(UserTreePath.depth <= max_depth)

            downline = session.exec(query).all()
            return list(downline)

        except Exception as e:
            print(f"❌ Error obteniendo downline: {e}")
            return []

    @staticmethod
    def get_level_members(session, member_id: int, level: int) -> List[Users]:
        """
        Obtiene todos los miembros de un nivel específico.

        Args:
            session: Sesión de base de datos
            member_id: member_id del usuario
            level: Nivel específico (1=hijos directos, 2=nietos, etc.)

        Returns:
            List[Users]: Miembros en ese nivel exacto

        Uso:
            - Nivel 1 para Bono Rápido (directos)
            - Niveles 1-7 para Bono Uninivel
        """
        try:
            members = session.exec(
                select(Users)
                .join(UserTreePath, Users.member_id == UserTreePath.descendant_id)
                .where(
                    UserTreePath.ancestor_id == member_id,
                    UserTreePath.depth == level
                )
            ).all()

            return list(members)

        except Exception as e:
            print(f"❌ Error obteniendo miembros del nivel {level}: {e}")
            return []

    @staticmethod
    def get_direct_referrals(session, member_id: int) -> List[Users]:
        """
        Obtiene solo los patrocinados directos (depth=1).
        Atajo para get_level_members(1).

        Args:
            session: Sesión de base de datos
            member_id: member_id del usuario

        Returns:
            List[Users]: Patrocinados directos
        """
        return GenealogyService.get_level_members(session, member_id, level=1)

    @staticmethod
    def count_downline(session, member_id: int, max_depth: Optional[int] = None) -> int:
        """
        Cuenta el total de descendientes sin cargar objetos User.
        Más eficiente que len(get_downline()).

        Args:
            session: Sesión de base de datos
            member_id: member_id del usuario
            max_depth: Profundidad máxima

        Returns:
            int: Total de descendientes
        """
        try:
            from sqlmodel import func

            query = (
                select(func.count(UserTreePath.descendant_id))
                .where(
                    UserTreePath.ancestor_id == member_id,
                    UserTreePath.depth > 0
                )
            )

            if max_depth is not None:
                query = query.where(UserTreePath.depth <= max_depth)

            count = session.exec(query).one()
            return count

        except Exception as e:
            print(f"❌ Error contando downline: {e}")
            return 0

    @staticmethod
    def is_ancestor(session, potential_ancestor: int, descendant: int) -> bool:
        """
        Verifica si un miembro es ancestro de otro.

        Args:
            session: Sesión de base de datos
            potential_ancestor: member_id del potencial ancestro
            descendant: member_id del descendiente

        Returns:
            bool: True si hay relación ancestro-descendiente
        """
        try:
            path = session.exec(
                select(UserTreePath).where(
                    UserTreePath.ancestor_id == potential_ancestor,
                    UserTreePath.descendant_id == descendant,
                    UserTreePath.depth > 0
                )
            ).first()

            return path is not None

        except Exception as e:
            print(f"❌ Error verificando ancestro: {e}")
            return False

    @staticmethod
    def get_all_ancestors(session, member_id: int) -> List[int]:
        """
        Obtiene todos los member_ids ancestros de un miembro (incluyendo self).

        Args:
            session: Sesión de base de datos
            member_id: member_id del usuario

        Returns:
            List[int]: Lista de member_ids ancestros (incluyendo self)
        """
        try:
            ancestor_ids = session.exec(
                select(UserTreePath.ancestor_id).where(
                    UserTreePath.descendant_id == member_id
                )
            ).all()

            return list(ancestor_ids)

        except Exception as e:
            print(f"❌ Error obteniendo ancestros: {e}")
            return []
