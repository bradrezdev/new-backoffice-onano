"""
Actualizar PVG del usuario 1 para probar con el ejemplo de los requisitos:
- Visionario con 10,500 PVG
- Siguiente rango: Emprendedor (21,000 PVG)
- Debería mostrar 50% de progreso
"""

import reflex as rx
import sqlmodel
from database.users import Users

print("\n" + "="*80)
print("🔧 Actualizar PVG del Usuario 1 para prueba")
print("="*80 + "\n")

member_id = 1
new_pvg = 10500

with rx.session() as session:
    user = session.exec(
        sqlmodel.select(Users).where(Users.member_id == member_id)
    ).first()
    
    if not user:
        print(f"❌ Usuario {member_id} no encontrado")
        exit(1)
    
    old_pvg = user.pvg_cache
    user.pvg_cache = new_pvg
    session.add(user)
    session.commit()
    
    print(f"✅ Usuario actualizado:")
    print(f"   Nombre: {user.first_name} {user.last_name}")
    print(f"   PVG anterior: {old_pvg:,}")
    print(f"   PVG nuevo: {new_pvg:,}")
    print()
    
    # Calcular progreso esperado
    next_rank_pvg = 21000  # Emprendedor
    progress = (new_pvg / next_rank_pvg) * 100
    
    print(f"📊 Progreso esperado:")
    print(f"   {new_pvg:,} / {next_rank_pvg:,} = {progress:.1f}%")
    print()

print("="*80)
print("✅ ACTUALIZACIÓN COMPLETADA")
print("="*80 + "\n")
