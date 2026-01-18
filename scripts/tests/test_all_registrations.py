#!/usr/bin/env python3
"""Script para diagnosticar por qué get_all_registrations retorna 0"""

from NNProtect_new_website.mlm_service.mlm_user_manager import MLMUserManager

# Probar con member_id = 1 (como en tu SQL)
member_id = 1

print(f"🔍 Probando get_all_registrations() con member_id={member_id}")
print("=" * 60)

# Llamar al método
result = MLMUserManager.get_all_registrations(member_id)

print(f"\n📊 Resultado:")
print(f"   - Total usuarios: {len(result)}")

if result:
    print(f"\n✅ Primeros 5 usuarios encontrados:")
    for i, user in enumerate(result[:5], 1):
        print(f"   {i}. member_id={user.get('member_id')}, nombre={user.get('full_name')}, nivel={user.get('level')}")
else:
    print("\n❌ No se encontraron usuarios")
    print("\n🔍 Posibles causas:")
    print("   1. La tabla UserTreePath está vacía")
    print("   2. El member_id 1 no tiene descendientes")
    print("   3. Los descendientes tienen depth=0 (self-reference)")
    
    print("\n💡 Ejecuta este SQL para verificar:")
    print("""
    SELECT COUNT(*) as total 
    FROM usertreepaths 
    WHERE ancestor_id = 1 AND depth > 0;
    """)
