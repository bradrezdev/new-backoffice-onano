"""
Script de testing para verificar el cálculo correcto de PVG.

Escenario de prueba:
A -> B -> C

C compra 100 PV → C tiene 100 PV y 100 PVG
B compra 200 PV → B tiene 200 PV y 300 PVG (200 propios + 100 de C)
A compra 400 PV → A tiene 400 PV y 700 PVG (400 propios + 200 de B + 100 de C)
"""

import reflex as rx
from database.users import Users
from database.usertreepaths import UserTreePath


def verify_pvg_calculation():
    """Verifica que el cálculo de PVG sea correcto."""

    with rx.session() as session:
        print("=" * 80)
        print("VERIFICACIÓN DE CÁLCULO DE PVG")
        print("=" * 80)

        # Buscar usuarios existentes
        user_a = session.exec(
            rx.select(Users).where(Users.member_id == 1)
        ).first()

        user_b = session.exec(
            rx.select(Users).where(Users.member_id == 2)
        ).first()

        user_c = session.exec(
            rx.select(Users).where(Users.member_id == 3)
        ).first()

        if not all([user_a, user_b, user_c]):
            print("❌ No se encontraron los 3 usuarios necesarios (member_id 1, 2, 3)")
            print("Por favor, crea primero la estructura de red A -> B -> C")
            return

        # Verificar estructura de red
        print("\n📊 ESTRUCTURA DE RED:")
        print(f"Usuario A (member_id=1): {user_a.first_name} {user_a.last_name}")
        print(f"Usuario B (member_id=2): {user_b.first_name} {user_b.last_name}")
        print(f"Usuario C (member_id=3): {user_c.first_name} {user_c.last_name}")

        # Mostrar valores actuales
        print("\n📈 VALORES ACTUALES:")
        print(f"A → PV: {user_a.pv_cache}, PVG: {user_a.pvg_cache}")
        print(f"B → PV: {user_b.pv_cache}, PVG: {user_b.pvg_cache}")
        print(f"C → PV: {user_c.pv_cache}, PVG: {user_c.pvg_cache}")

        # Verificar fórmula de PVG
        print("\n🔍 VERIFICACIÓN DE FÓRMULA PVG:")

        # Para C: PVG = PV propio (no tiene descendientes)
        expected_c_pvg = user_c.pv_cache
        print(f"C → Esperado: {expected_c_pvg}, Actual: {user_c.pvg_cache} {'✅' if user_c.pvg_cache == expected_c_pvg else '❌'}")

        # Para B: PVG = PV propio + PV de descendientes (C)
        expected_b_pvg = user_b.pv_cache + user_c.pv_cache
        print(f"B → Esperado: {expected_b_pvg} ({user_b.pv_cache} + {user_c.pv_cache}), Actual: {user_b.pvg_cache} {'✅' if user_b.pvg_cache == expected_b_pvg else '❌'}")

        # Para A: PVG = PV propio + PV de todos los descendientes (B + C)
        expected_a_pvg = user_a.pv_cache + user_b.pv_cache + user_c.pv_cache
        print(f"A → Esperado: {expected_a_pvg} ({user_a.pv_cache} + {user_b.pv_cache} + {user_c.pv_cache}), Actual: {user_a.pvg_cache} {'✅' if user_a.pvg_cache == expected_a_pvg else '❌'}")

        # Verificar genealogía
        print("\n🌳 GENEALOGÍA:")
        paths = session.exec(
            rx.select(UserTreePath).order_by(UserTreePath.ancestor_id, UserTreePath.descendant_id)
        ).all()

        for path in paths:
            ancestor = session.exec(rx.select(Users).where(Users.member_id == path.ancestor_id)).first()
            descendant = session.exec(rx.select(Users).where(Users.member_id == path.descendant_id)).first()
            print(f"  {ancestor.first_name} -> {descendant.first_name} (depth={path.depth})")

        print("\n" + "=" * 80)


if __name__ == "__main__":
    verify_pvg_calculation()
