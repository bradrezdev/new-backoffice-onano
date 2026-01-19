"""
Script para crear estructura 3x3 de usuarios a 5 niveles de profundidad.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import reflex as rx
import sqlmodel
from database.users import Users, UserStatus
from database.usertreepaths import UserTreePath
from NNProtect_new_website.modules.network.backend.genealogy_service import GenealogyService
from datetime import datetime, timezone


def create_3x3_structure():
    """Crea estructura 2x2 a 3 niveles de profundidad (optimizado para velocidad)."""

    print("=" * 80)
    print("CREANDO ESTRUCTURA 2x2 A 3 NIVELES (OPTIMIZADO)")
    print("=" * 80)

    with rx.session() as session:
        # Obtener el siguiente member_id disponible
        last_user = session.exec(
            sqlmodel.select(Users).order_by(sqlmodel.desc(Users.member_id))
        ).first()

        next_member_id = last_user.member_id + 1 if last_user else 2

        print(f"\n📊 Último member_id: {last_user.member_id if last_user else 1}")
        print(f"📊 Siguiente member_id disponible: {next_member_id}")

        # Estructura optimizada: cada nodo tiene 2 hijos
        # Nivel 1: 2 usuarios (hijos de member_id=1)
        # Nivel 2: 4 usuarios (2 hijos por cada nodo de nivel 1)
        # Nivel 3: 8 usuarios (2 hijos por cada nodo de nivel 2)
        # Total: 2 + 4 + 8 = 14 usuarios

        created_users = []
        current_id = next_member_id

        # Crear usuarios por nivel
        parent_queue = [1]  # Empezar con member_id=1 como raíz

        for level in range(1, 4):  # 3 niveles
            print(f"\n🔄 Creando usuarios de Nivel {level}...")

            new_parents = []

            for parent_id in parent_queue:
                # Crear 2 hijos para cada padre
                for child_num in range(1, 3):
                    # Crear usuario
                    new_user = Users(
                        member_id=current_id,
                        first_name=f"Usuario",
                        last_name=f"L{level}_{current_id}",
                        email_cache=f"user{current_id}@test.com",
                        status=UserStatus.NO_QUALIFIED,
                        sponsor_id=parent_id,
                        created_at=datetime.now(timezone.utc)
                    )

                    session.add(new_user)
                    session.flush()

                    # Crear genealogía
                    GenealogyService.add_member_to_tree(
                        session,
                        new_member_id=current_id,
                        sponsor_id=parent_id
                    )

                    created_users.append({
                        "member_id": current_id,
                        "level": level,
                        "parent_id": parent_id
                    })

                    new_parents.append(current_id)
                    current_id += 1

            parent_queue = new_parents
            print(f"   ✅ Creados {len(new_parents)} usuarios en Nivel {level}")

            # Commit intermedio por nivel para mejor rendimiento
            session.commit()

        print(f"\n✅ Total de usuarios creados: {len(created_users)}")

        # Verificar la estructura
        print("\n🔍 Verificando estructura creada:")
        print("-" * 80)

        for level in range(1, 4):
            count = sum(1 for u in created_users if u['level'] == level)
            print(f"   Nivel {level}: {count} usuarios")

        # Verificar UserTreePath
        total_paths = session.exec(
            sqlmodel.select(sqlmodel.func.count(UserTreePath.ancestor_id))
        ).one()

        print(f"\n📊 Total de registros en UserTreePath: {total_paths}")

        # Verificar descendientes de member_id=1
        descendants_1 = session.exec(
            sqlmodel.select(UserTreePath)
            .where(
                UserTreePath.ancestor_id == 1,
                UserTreePath.depth > 0
            )
        ).all()

        print(f"📊 Descendientes de member_id=1: {len(descendants_1)}")

    print("\n" + "=" * 80)
    print("✅ ESTRUCTURA CREADA EXITOSAMENTE")
    print("=" * 80)


if __name__ == "__main__":
    create_3x3_structure()
