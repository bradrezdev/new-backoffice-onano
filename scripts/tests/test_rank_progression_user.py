"""
Test de progresión de rango con usuario real (member_id=1)
"""

import reflex as rx
import sqlmodel
from database.users import Users
from database.user_rank_history import UserRankHistory
from database.ranks import Ranks
from datetime import datetime, timezone

print("\n" + "="*80)
print("🧪 TEST: Progresión de Rango - Usuario Real (Member ID: 1)")
print("="*80 + "\n")

member_id = 1

with rx.session() as session:
    # 1. Obtener datos del usuario
    user = session.exec(
        sqlmodel.select(Users).where(Users.member_id == member_id)
    ).first()
    
    if not user:
        print(f"❌ Usuario {member_id} no encontrado")
        exit(1)
    
    print(f"👤 Usuario: {user.first_name} {user.last_name}")
    print(f"📊 PVG actual: {user.pvg_cache:,}")
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
    
    if current_rank_history:
        current_rank = session.exec(
            sqlmodel.select(Ranks).where(Ranks.id == current_rank_history.rank_id)
        ).first()
        print(f"🎖️  Rango actual: {current_rank.name} (ID: {current_rank.id})")
        print(f"   PVG requerido para este rango: {current_rank.pvg_required:,}")
    else:
        print("⚠️  No se encontró rango del mes actual, usando 'Sin rango' por defecto")
        current_rank_history = type('obj', (object,), {'rank_id': 1})()
        current_rank = session.exec(
            sqlmodel.select(Ranks).where(Ranks.id == 1)
        ).first()
        print(f"🎖️  Rango actual: {current_rank.name} (ID: {current_rank.id})")
    
    print()
    
    # 3. Obtener siguiente rango
    next_rank = session.exec(
        sqlmodel.select(Ranks)
        .where(Ranks.id == current_rank_history.rank_id + 1)
        .order_by(Ranks.id)
    ).first()
    
    if next_rank:
        print(f"🎯 Siguiente rango: {next_rank.name} (ID: {next_rank.id})")
        print(f"   PVG requerido: {next_rank.pvg_required:,}")
        print()
        
        # 4. Calcular progreso
        current_pvg = user.pvg_cache or 0
        next_rank_pvg = next_rank.pvg_required
        
        if next_rank_pvg > 0:
            progress_percentage = (current_pvg / next_rank_pvg) * 100
        else:
            progress_percentage = 0.0
        
        print("="*80)
        print("📊 RESULTADO PARA EL DASHBOARD:")
        print("="*80)
        print(f"Texto a mostrar: '{current_pvg:,} — {next_rank_pvg:,} PVG'")
        print(f"Progreso de barra: {progress_percentage:.2f}%")
        print()
        
        # Visualización de barra
        bar_length = 50
        filled = int(bar_length * progress_percentage / 100)
        empty = bar_length - filled
        bar = "█" * filled + "░" * empty
        
        print(f"Barra visual: [{bar}] {progress_percentage:.1f}%")
        print()
        
    else:
        print("🏆 Usuario está en el rango máximo!")
        print()

print("="*80)
print("✅ TEST COMPLETADO")
print("="*80 + "\n")
