"""
Servicio para resetear usuarios al inicio de un nuevo período.
Principios aplicados: KISS, DRY, YAGNI, POO
"""

import sqlmodel
from datetime import datetime, timezone
from typing import Optional

from database.users import Users, UserStatus
from database.user_rank_history import UserRankHistory


class PeriodResetService:
    """
    Servicio POO para resetear usuarios al inicio de período.
    Principio DRY: Centraliza la lógica de reseteo en un solo lugar.
    """

    @classmethod
    def reset_all_users_for_new_period(
        cls,
        session: sqlmodel.Session,
        new_period_id: int
    ) -> int:
        """
        Resetea TODOS los usuarios para el nuevo período.
        
        Acciones (según requisitos):
        1. status → NO_QUALIFIED
        2. pv_cache → 0
        3. pvg_cache → 0
        4. vn_cache → 0
        5. Asignar rank_id=1 en user_rank_history con nuevo period_id
        
        Principio KISS: Proceso lineal y claro.
        
        Args:
            session: Sesión de base de datos
            new_period_id: ID del nuevo período
            
        Returns:
            Cantidad de usuarios reseteados
        """
        try:
            # 1. Obtener TODOS los usuarios
            all_users = session.exec(
                sqlmodel.select(Users)
            ).all()
            
            if not all_users:
                print("⚠️  No hay usuarios para resetear")
                return 0
            
            print(f"\n🔄 Reseteando {len(all_users)} usuarios para nuevo período...")
            
            resetted_count = 0
            
            for user in all_users:
                # 2. Resetear campos del usuario
                user.status = UserStatus.NO_QUALIFIED
                user.pv_cache = 0
                user.pvg_cache = 0
                user.vn_cache = 0.0
                user.updated_at = datetime.now(timezone.utc)
                
                session.add(user)
                
                # 3. Crear registro en user_rank_history con rank_id=1
                rank_history = UserRankHistory(
                    member_id=user.member_id,
                    rank_id=1,  # Rank "Sin rango" o inicial
                    achieved_on=datetime.now(timezone.utc),
                    period_id=new_period_id
                )
                
                session.add(rank_history)
                resetted_count += 1
            
            session.flush()
            
            print(f"✅ {resetted_count} usuarios reseteados exitosamente")
            return resetted_count
            
        except Exception as e:
            print(f"❌ Error reseteando usuarios: {e}")
            import traceback
            traceback.print_exc()
            return 0
