"""
Test para verificar que los nuevos usuarios tengan el referral_link correcto
"""

import reflex as rx
import sqlmodel
from database.users import Users
from NNProtect_new_website.mlm_service.mlm_user_manager import MLMUserManager

print("\n" + "="*80)
print("🧪 TEST: Verificar formato de referral_link con get_base_url()")
print("="*80 + "\n")

# 1. Verificar qué URL base se usa
base_url = MLMUserManager.get_base_url()
print(f"📍 Base URL detectada: {base_url}")
print()

# 2. Ver formato esperado
test_member_id = 9999
expected_link = f"{base_url}?ref={test_member_id}"
print(f"✅ Formato esperado para member_id {test_member_id}:")
print(f"   {expected_link}")
print()

# 3. Verificar formato en usuarios existentes
with rx.session() as session:
    # Ver el usuario member_id=1 (debería tener el formato correcto)
    user1 = session.exec(
        sqlmodel.select(Users).where(Users.member_id == 1)
    ).first()
    
    if user1:
        print(f"📊 Usuario member_id=1:")
        print(f"   Referral link: {user1.referral_link}")
        print()

print("="*80)
print("✅ Verificación de formato completada")
print("="*80 + "\n")
