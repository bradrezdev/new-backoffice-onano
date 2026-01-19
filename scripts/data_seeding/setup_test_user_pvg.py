"""
Script: Asignar PVG a un usuario para probar la progresión de rango
"""

import reflex as rx
import sqlmodel
from database.users import Users
from database.user_rank_history import UserRankHistory
from database.ranks import Ranks
from datetime import datetime, timezone

print("\n" + "="*80)
print("🔧 SETUP: Asignar PVG a usuario para test")
print("="*80 + "\n")

def setup_test_user(member_id: int, pvg_amount: int, target_rank_id: int = 2):
    """
    Configura un usuario de prueba con PVG y rango específicos.
    
    Args:
        member_id: ID del usuario
        pvg_amount: Cantidad de PVG a asignar
        target_rank_id: Rank ID a asignar (por defecto 2 = Visionario)
    """
    try:
        with rx.session() as session:
            # Obtener usuario
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()
            
            if not user:
                print(f"❌ Usuario {member_id} no encontrado")
                return False
            
            print(f"👤 Usuario encontrado: {user.first_name} {user.last_name} (ID: {member_id})")
            print(f"   PVG actual: {user.pvg_cache or 0:,}")
            print()
            
            # Actualizar PVG
            user.pvg_cache = pvg_amount
            session.add(user)
            print(f"✅ PVG actualizado a: {pvg_amount:,}")
            
            # Obtener información del rango
            rank = session.exec(
                sqlmodel.select(Ranks).where(Ranks.id == target_rank_id)
            ).first()
            
            if not rank:
                print(f"❌ Rango {target_rank_id} no encontrado")
                return False
            
            print(f"🏆 Asignando rango: {rank.name} (ID: {target_rank_id})")
            
            # Verificar si ya tiene registro de rango para este mes
            now = datetime.now(timezone.utc)
            existing_rank = session.exec(
                sqlmodel.select(UserRankHistory)
                .where(
                    UserRankHistory.member_id == member_id,
                    UserRankHistory.rank_id == target_rank_id,
                    sqlmodel.extract('year', UserRankHistory.achieved_on) == now.year,
                    sqlmodel.extract('month', UserRankHistory.achieved_on) == now.month
                )
            ).first()
            
            if not existing_rank:
                # Crear nuevo registro de rango
                rank_history = UserRankHistory(
                    member_id=member_id,
                    rank_id=target_rank_id,
                    achieved_on=now
                )
                session.add(rank_history)
                print(f"✅ Registro de rango creado para el mes actual")
            else:
                print(f"ℹ️  Ya existe registro de rango {rank.name} para este mes")
            
            session.commit()
            print()
            
            # Calcular siguiente rango
            next_rank = session.exec(
                sqlmodel.select(Ranks)
                .where(Ranks.id == target_rank_id + 1)
            ).first()
            
            if next_rank:
                progress = int((pvg_amount / next_rank.pvg_required) * 100)
                print("📈 PROGRESIÓN CALCULADA:")
                print(f"   Rango actual: {rank.name} (PVG requerido: {rank.pvg_required:,})")
                print(f"   Siguiente rango: {next_rank.name} (PVG requerido: {next_rank.pvg_required:,})")
                print(f"   Texto esperado: {pvg_amount:,} — {next_rank.pvg_required:,} PVG")
                print(f"   Progreso: {progress}%")
                
                # Visualización
                bar_length = 50
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"   [{bar}] {progress}%")
            else:
                print(f"🏅 Usuario está en rango máximo: {rank.name}")
            
            print()
            print("="*80)
            print("✅ SETUP COMPLETADO")
            print("="*80)
            return True
            
    except Exception as e:
        print(f"❌ Error en setup: {e}")
        import traceback
        traceback.print_exc()
        return False

# Configurar usuario 1 con el ejemplo de los requisitos:
# Visionario con 10,500 PVG
print("🎯 Configurando usuario según ejemplo de requisitos:")
print("   - Rango: Visionario (ID: 2)")
print("   - PVG: 10,500")
print("   - Siguiente rango: Emprendedor (21,000 PVG)")
print("   - Progreso esperado: 50%")
print()

success = setup_test_user(
    member_id=1,
    pvg_amount=10500,
    target_rank_id=2  # Visionario
)

if success:
    print("\n💡 SIGUIENTE PASO:")
    print("   1. Inicia sesión con el usuario ID 1 en el dashboard")
    print("   2. Verifica que la sección 'Progresión siguiente rango' muestre:")
    print("      - Texto: '10,500 — 21,000 PVG'")
    print("      - Barra de progreso al 50%")
    print()
