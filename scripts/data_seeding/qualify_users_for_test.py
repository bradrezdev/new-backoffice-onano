"""
Script para calificar algunos usuarios y probar el balance de colores en el dashboard
"""

import reflex as rx
import sqlmodel
from database.users import Users, UserStatus
import random

print("\n" + "="*80)
print("🔧 Calificando usuarios para prueba de dashboard")
print("="*80 + "\n")

with rx.session() as session:
    # Obtener todos los usuarios no calificados
    non_qualified_users = session.exec(
        sqlmodel.select(Users)
        .where(Users.status == UserStatus.NO_QUALIFIED)
        .limit(300)  # Calificar ~30% de 1032 usuarios
    ).all()
    
    print(f"📊 Encontrados {len(non_qualified_users)} usuarios no calificados")
    print(f"🎯 Calificando aproximadamente 300 usuarios (~29%)...")
    print()
    
    # Calificar usuarios
    qualified_count = 0
    for user in non_qualified_users:
        user.status = UserStatus.QUALIFIED
        session.add(user)
        qualified_count += 1
    
    session.commit()
    
    print(f"✅ {qualified_count} usuarios calificados")
    print()
    
    # Verificar nuevo balance
    total_qualified = session.exec(
        sqlmodel.select(sqlmodel.func.count(Users.id))
        .where(Users.status == UserStatus.QUALIFIED)
    ).first() or 0
    
    total_non_qualified = session.exec(
        sqlmodel.select(sqlmodel.func.count(Users.id))
        .where(Users.status == UserStatus.NO_QUALIFIED)
    ).first() or 0
    
    total = total_qualified + total_non_qualified
    
    qualified_pct = (total_qualified / total) * 100 if total > 0 else 0
    non_qualified_pct = (total_non_qualified / total) * 100 if total > 0 else 0
    
    print("📊 NUEVO BALANCE:")
    print("-" * 80)
    print(f"{'Tipo':<25} {'Cantidad':<15} {'Porcentaje'}")
    print("-" * 80)
    print(f"{'Calificados':<25} {total_qualified:<15} {qualified_pct:.1f}%")
    print(f"{'No calificados':<25} {total_non_qualified:<15} {non_qualified_pct:.1f}%")
    print("-" * 80)
    print(f"{'TOTAL':<25} {total:<15} 100.0%")
    print()
    
    # Visualización
    green_bar_length = int((qualified_pct / 100) * 50)
    red_bar_length = int((non_qualified_pct / 100) * 50)
    
    green_bar = "█" * green_bar_length
    red_bar = "█" * red_bar_length
    
    print("🎨 VISUALIZACIÓN:")
    print("-" * 80)
    print(f"Verde: {green_bar} {qualified_pct:.1f}%")
    print(f"Roja:  {red_bar} {non_qualified_pct:.1f}%")
    print()

print("="*80)
print("✅ Usuarios calificados - Ahora el dashboard mostrará un balance")
print("="*80 + "\n")
