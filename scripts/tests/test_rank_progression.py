"""
Test: Progresión de rango del usuario
Verifica que se calculen correctamente los PVG actuales, PVG necesarios y el porcentaje.
"""

import reflex as rx
import sqlmodel
from database.users import Users
from database.user_rank_history import UserRankHistory
from database.ranks import Ranks
from datetime import datetime, timezone

print("\n" + "="*80)
print("🧪 TEST: Progresión de Rango del Usuario")
print("="*80 + "\n")

def test_rank_progression(member_id: int):
    """Prueba la progresión de rango para un usuario específico."""
    try:
        with rx.session() as session:
            # 1. Obtener usuario y PVG actual
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()
            
            if not user:
                print(f"❌ Usuario {member_id} no encontrado")
                return
            
            current_pvg = user.pvg_cache or 0
            print(f"👤 Usuario: {user.first_name} {user.last_name} (ID: {member_id})")
            print(f"📊 PVG Actual: {current_pvg:,}")
            print()
            
            # 2. Obtener rank_id actual del mes
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
            
            # Obtener nombre del rango actual
            current_rank = session.exec(
                sqlmodel.select(Ranks).where(Ranks.id == current_rank_id)
            ).first()
            
            if current_rank:
                print(f"🏆 Rango Actual: {current_rank.name} (ID: {current_rank_id})")
                print(f"   PVG Requerido: {current_rank.pvg_required:,}")
            else:
                print(f"⚠️  Rango actual no encontrado (ID: {current_rank_id})")
            print()
            
            # 3. Obtener siguiente rango
            next_rank = session.exec(
                sqlmodel.select(Ranks)
                .where(Ranks.id == current_rank_id + 1)
                .order_by(Ranks.id)
            ).first()
            
            if next_rank:
                next_rank_pvg = next_rank.pvg_required
                print(f"🎯 Siguiente Rango: {next_rank.name} (ID: {next_rank.id})")
                print(f"   PVG Requerido: {next_rank_pvg:,}")
                print()
                
                # 4. Calcular progreso
                if next_rank_pvg > 0:
                    progress_percentage = int((current_pvg / next_rank_pvg) * 100)
                else:
                    progress_percentage = 0
                
                print("📈 PROGRESIÓN:")
                print(f"   {current_pvg:,} — {next_rank_pvg:,} PVG")
                print(f"   Progreso: {progress_percentage}%")
                print()
                
                # Visualización de la barra
                bar_length = 50
                filled = int(bar_length * progress_percentage / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"   [{bar}] {progress_percentage}%")
                print()
                
                # Faltante
                remaining = next_rank_pvg - current_pvg
                if remaining > 0:
                    print(f"   Faltan: {remaining:,} PVG para alcanzar {next_rank.name}")
                else:
                    print(f"   ✅ Ya alcanzaste el PVG requerido para {next_rank.name}!")
            else:
                print("🏅 ¡Usuario está en el rango máximo!")
                if current_rank:
                    print(f"   Rango: {current_rank.name}")
                    print(f"   PVG: {current_pvg:,} / {current_rank.pvg_required:,}")
                    print(f"   Progreso: 100%")
            
            print()
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

# Probar con algunos usuarios
print("🔍 Probando con usuarios de ejemplo...\n")

# Usuario de prueba 1 (ajusta este ID según tu base de datos)
test_member_ids = [1, 2, 3]

for member_id in test_member_ids:
    test_rank_progression(member_id)
    print("-" * 80)
    print()

print("="*80)
print("✅ TEST COMPLETADO")
print("="*80 + "\n")
