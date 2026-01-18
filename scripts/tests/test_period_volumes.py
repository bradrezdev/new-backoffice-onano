#!/usr/bin/env python3
"""Script para probar get_period_volumes()"""

from NNProtect_new_website.mlm_service.mlm_user_manager import MLMUserManager

# Probar con member_id = 1
member_id = 1

print(f"🧪 Probando get_period_volumes() con member_id={member_id}")
print("=" * 70)

result = MLMUserManager.get_period_volumes(member_id)

if result:
    print(f"\n✅ Obtenidos {len(result)} periodos\n")
    
    for period in result:
        print(f"📅 Periodo: {period['period_name']}")
        print(f"   PV Personal: {period['volumes']['pv']:,.2f}")
        for level in range(1, 10):
            vol = period['volumes'].get(f'level_{level}', 0)
            print(f"   Nivel {level}: {vol:,.2f}")
        print()
else:
    print("\n❌ No se obtuvieron datos")
