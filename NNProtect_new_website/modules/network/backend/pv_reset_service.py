"""
Servicio POO para reseteo mensual de PV/PVG y ajuste de rangos.
Maneja el reseteo automático el día 1 de cada mes.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import sqlmodel
from typing import List

from database.users import Users
from .rank_service import RankService


class PVResetService:
    """
    Servicio POO para reseteo mensual de PV/PVG.
    Principio POO: Encapsula lógica de reseteo y ajuste de rangos.
    """

    @classmethod
    def reset_all_users_pv_pvg(cls, session) -> int:
        """
        Resetea PV_cache y PVG_cache de todos los usuarios a 0.
        Principio KISS: Operación directa sin complejidad.

        Returns:
            Número de usuarios reseteados
        """
        try:
            # Obtener todos los usuarios
            all_users = session.exec(
                sqlmodel.select(Users)
            ).all()

            reset_count = 0
            for user in all_users:
                user.pv_cache = 0
                user.pvg_cache = 0
                session.add(user)
                reset_count += 1

            session.flush()
            print(f"✅ PV/PVG reseteado para {reset_count} usuarios")
            return reset_count

        except Exception as e:
            print(f"❌ Error reseteando PV/PVG: {e}")
            raise

    @classmethod
    def adjust_all_user_ranks(cls, session) -> int:
        """
        Ajusta los rangos de todos los usuarios después del reseteo.
        Como PV/PVG están en 0, todos volverán al rango "Sin rango".

        Principio DRY: Usa RankService.check_and_update_rank() para cada usuario.

        Returns:
            Número de usuarios cuyo rango fue ajustado
        """
        try:
            # Obtener todos los usuarios
            all_users = session.exec(
                sqlmodel.select(Users)
            ).all()

            adjusted_count = 0
            for user in all_users:
                # Verificar y actualizar rango según PV/PVG actual (que será 0)
                rank_changed = RankService.check_and_update_rank(session, user.member_id)
                if rank_changed:
                    adjusted_count += 1

            print(f"✅ Rangos ajustados para {adjusted_count} usuarios")
            return adjusted_count

        except Exception as e:
            print(f"❌ Error ajustando rangos: {e}")
            raise

    @classmethod
    def monthly_reset_and_rank_adjustment(cls, session) -> bool:
        """
        Ejecuta el proceso completo de reseteo mensual:
        1. Resetea PV/PVG de todos los usuarios a 0
        2. Ajusta rangos de todos los usuarios según sus nuevos valores

        Principio POO: Método orquestador que coordina el proceso completo.

        Returns:
            True si se ejecutó correctamente, False si falló
        """
        try:
            print("🔄 Iniciando reseteo mensual de PV/PVG...")

            # Paso 1: Resetear PV/PVG
            reset_count = cls.reset_all_users_pv_pvg(session)

            # Paso 2: Ajustar rangos
            adjusted_count = cls.adjust_all_user_ranks(session)

            session.commit()
            print(f"✅ Reseteo mensual completado: {reset_count} usuarios reseteados, {adjusted_count} rangos ajustados")
            return True

        except Exception as e:
            session.rollback()
            print(f"❌ Error en reseteo mensual: {e}")
            import traceback
            traceback.print_exc()
            return False
