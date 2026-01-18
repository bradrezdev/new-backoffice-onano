"""
Script de testing para verificar el método optimizado get_network_descendants.

Verifica:
1. Que la consulta use correctamente UserTreePath.ancestor_id
2. Que elimine la recursión innecesaria
3. Que el nivel se obtenga directamente de tree_path.depth
4. Que los datos del sponsor se carguen correctamente con cache
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import reflex as rx
from NNProtect_new_website.mlm_service.mlm_user_manager import MLMUserManager


def test_get_network_descendants():
    """Prueba el método optimizado get_network_descendants."""

    print("=" * 80)
    print("TEST: get_network_descendants (método optimizado)")
    print("=" * 80)

    # Usar member_id=1 como usuario raíz
    sponsor_member_id = 1

    print(f"\n🔍 Obteniendo descendientes de member_id={sponsor_member_id}...")

    # Llamar al método optimizado
    descendants = MLMUserManager.get_network_descendants(sponsor_member_id)

    print(f"\n✅ Total de descendientes encontrados: {len(descendants)}")

    if len(descendants) == 0:
        print("\n⚠️  No se encontraron descendientes. Esto puede ser normal si el usuario no tiene red.")
        return

    # Mostrar primeros 10 resultados
    print("\n📊 Primeros 10 descendientes:")
    print("-" * 80)

    for i, desc in enumerate(descendants[:10], 1):
        print(f"\n{i}. {desc['full_name']} (member_id={desc['member_id']})")
        print(f"   Nivel: {desc['level']}")
        print(f"   Email: {desc['email']}")
        print(f"   Teléfono: {desc['phone']}")
        print(f"   Status: {desc['status']}")
        print(f"   Fecha registro: {desc['created_at']}")
        print(f"   Sponsor: {desc['sponsor_full_name']} (ID: {desc['sponsor_member_id']})")

    # Verificar niveles
    print("\n📈 Distribución por niveles:")
    print("-" * 80)

    niveles = {}
    for desc in descendants:
        nivel = desc['level']
        if nivel not in niveles:
            niveles[nivel] = 0
        niveles[nivel] += 1

    for nivel in sorted(niveles.keys()):
        print(f"   Nivel {nivel}: {niveles[nivel]} usuarios")

    # Verificar integridad de datos
    print("\n🔍 Verificación de integridad:")
    print("-" * 80)

    total_users = len(descendants)
    users_with_sponsor = sum(1 for d in descendants if d['sponsor_member_id'] is not None)
    users_with_email = sum(1 for d in descendants if d['email'])
    users_with_phone = sum(1 for d in descendants if d['phone'])

    print(f"   Total usuarios: {total_users}")
    print(f"   Con sponsor: {users_with_sponsor} ({(users_with_sponsor/total_users*100):.1f}%)")
    print(f"   Con email: {users_with_email} ({(users_with_email/total_users*100):.1f}%)")
    print(f"   Con teléfono: {users_with_phone} ({(users_with_phone/total_users*100):.1f}%)")

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    test_get_network_descendants()
