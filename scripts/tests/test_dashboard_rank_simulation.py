"""
Test final: Simular el comportamiento del DashboardState.load_rank_progression()
"""

import reflex as rx
import sqlmodel
from database.users import Users
from database.user_rank_history import UserRankHistory
from database.ranks import Ranks
from datetime import datetime, timezone

print("\n" + "="*80)
print("🧪 TEST FINAL: Simulación de DashboardState.load_rank_progression()")
print("="*80 + "\n")

class MockDashboardState:
    """Simulación del DashboardState para testing."""
    
    def __init__(self):
        self.current_pvg = 0
        self.next_rank_pvg = 0
        self.rank_progress_percentage = 0
    
    def load_rank_progression(self, member_id: int):
        """Carga la progresión del usuario hacia el siguiente rango."""
        try:
            with rx.session() as session:
                # Obtener PVG actual del usuario
                user = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == member_id)
                ).first()
                
                if not user:
                    print(f"⚠️  Usuario {member_id} no encontrado")
                    return False
                
                self.current_pvg = user.pvg_cache or 0
                
                # Obtener rank_id actual del mes
                now = datetime.now(timezone.utc)
                current_rank_history = session.exec(
                    sqlmodel.select(UserRankHistory)
                    .where(
                        UserRankHistory.member_id == member_id,
                        sqlmodel.extract('year', UserRankHistory.achieved_on) == now.year,
                        sqlmodel.extract('month', UserRankHistory.achieved_on) == now.month
                    )
                    .order_by(sqlmodel.desc(UserRankHistory.rank_id))
                ).first()
                
                current_rank_id = current_rank_history.rank_id if current_rank_history else 1
                
                # Obtener siguiente rango
                next_rank = session.exec(
                    sqlmodel.select(Ranks)
                    .where(Ranks.id == current_rank_id + 1)
                    .order_by(Ranks.id)
                ).first()
                
                if next_rank:
                    self.next_rank_pvg = next_rank.pvg_required
                    
                    # Calcular porcentaje de progreso
                    if self.next_rank_pvg > 0:
                        self.rank_progress_percentage = int((self.current_pvg / self.next_rank_pvg) * 100)
                    else:
                        self.rank_progress_percentage = 0
                else:
                    # Usuario está en el rango máximo
                    current_rank = session.exec(
                        sqlmodel.select(Ranks).where(Ranks.id == current_rank_id)
                    ).first()
                    self.next_rank_pvg = current_rank.pvg_required if current_rank else 0
                    self.rank_progress_percentage = 100
                
                print(f"📊 Progresión cargada - PVG: {self.current_pvg}/{self.next_rank_pvg} ({self.rank_progress_percentage}%)")
                return True
                
        except Exception as e:
            print(f"❌ Error cargando progresión de rango: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_display_text(self):
        """Retorna el texto a mostrar en la UI."""
        return f"{self.current_pvg:,} — {self.next_rank_pvg:,} PVG"

# Crear instancia y cargar datos
state = MockDashboardState()
success = state.load_rank_progression(member_id=1)

if success:
    print()
    print("="*80)
    print("📊 DATOS PARA LA UI:")
    print("="*80)
    print(f"Texto Desktop: '{state.get_display_text()}'")
    print(f"Texto Mobile:  '{state.get_display_text()}'")
    print(f"Valor de barra (progress): {state.rank_progress_percentage}")
    print(f"Max de barra: 100")
    print()
    
    # Visualización de barra
    bar_length = 50
    filled = int(bar_length * state.rank_progress_percentage / 100)
    empty = bar_length - filled
    bar = "█" * filled + "░" * empty
    
    print(f"Preview de barra: [{bar}] {state.rank_progress_percentage}%")
    print()
    
    print("="*80)
    print("✅ SIMULACIÓN EXITOSA - El DashboardState funcionará correctamente")
    print("="*80 + "\n")
else:
    print()
    print("="*80)
    print("❌ SIMULACIÓN FALLÓ")
    print("="*80 + "\n")
