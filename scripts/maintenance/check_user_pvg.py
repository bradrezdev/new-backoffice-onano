"""
Verificar el PVG real del usuario 1
"""

import reflex as rx
import sqlmodel
from database.users import Users

print("\n" + "="*80)
print("🔍 Verificar PVG del Usuario 1")
print("="*80 + "\n")

with rx.session() as session:
    user = session.exec(
        sqlmodel.select(Users).where(Users.member_id == 1)
    ).first()
    
    if user:
        print(f"👤 Usuario: {user.first_name} {user.last_name}")
        print(f"📊 PV (Personal): {user.pv_cache:,}")
        print(f"📊 PVG (Grupal): {user.pvg_cache:,}")
        print(f"📊 VN: {user.vn_cache:,}")
        print()
    else:
        print("❌ Usuario no encontrado")

print("="*80 + "\n")
