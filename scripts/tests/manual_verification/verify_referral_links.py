"""
Verificar el formato del referral_link en la base de datos
"""

import reflex as rx
import sqlmodel
from database.users import Users

with rx.session() as session:
    # Obtener los últimos 3 usuarios
    users = session.exec(
        sqlmodel.select(Users)
        .order_by(sqlmodel.desc(Users.member_id))
        .limit(3)
    ).all()
    
    print("\n" + "="*80)
    print("🔍 VERIFICACIÓN DE REFERRAL_LINK")
    print("="*80 + "\n")
    
    print(f"{'Member ID':<12} {'Referral Link'}")
    print("-" * 80)
    
    for user in reversed(users):
        print(f"{user.member_id:<12} {user.referral_link}")
    
    print("\n" + "="*80)
    print("✅ Verificación completada")
    print("="*80 + "\n")
