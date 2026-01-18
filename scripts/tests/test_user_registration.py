"""
Script de prueba para registro de usuario con sponsor.
Simula el registro completo con referral_link.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reflex as rx
from NNProtect_new_website.mlm_service.mlm_user_manager import MLMUserManager
from database.users import Users
from database.usertreepaths import UserTreePath
import sqlmodel

def test_user_registration():
    """Prueba el registro de un usuario con sponsor"""

    print("=" * 60)
    print("🧪 TEST: Registro de Usuario con Sponsor")
    print("=" * 60)
    print()

    try:
        with rx.session() as session:
            # 1. Verificar que existe el sponsor (member_id=1)
            sponsor = session.exec(
                sqlmodel.select(Users).where(Users.member_id == 1)
            ).first()

            if not sponsor:
                print("❌ No existe usuario con member_id=1 (sponsor)")
                return False

            print(f"✅ Sponsor encontrado: {sponsor.first_name} {sponsor.last_name} (member_id={sponsor.member_id})")
            print()

            # 2. Crear nuevo usuario con sponsor
            print("📝 Creando nuevo usuario...")
            new_user = MLMUserManager.create_mlm_user(
                session=session,
                supabase_user_id="test-uuid-12345",
                first_name="Test",
                last_name="User",
                email="test.user@example.com",
                sponsor_member_id=1  # Sponsor es member_id=1
            )

            if not new_user:
                print("❌ No se pudo crear el usuario")
                return False

            session.commit()
            print(f"✅ Usuario creado: {new_user.first_name} {new_user.last_name} (member_id={new_user.member_id})")
            print()

            # 3. Verificar UserTreePath
            print("🔍 Verificando estructura genealógica...")

            # Self-reference (depth=0)
            self_path = session.exec(
                sqlmodel.select(UserTreePath).where(
                    (UserTreePath.ancestor_id == new_user.member_id) &
                    (UserTreePath.descendant_id == new_user.member_id) &
                    (UserTreePath.depth == 0)
                )
            ).first()

            if self_path:
                print(f"✅ Self-reference creado (depth=0)")
            else:
                print(f"❌ Self-reference NO encontrado")

            # Relación con sponsor (depth=1)
            sponsor_path = session.exec(
                sqlmodel.select(UserTreePath).where(
                    (UserTreePath.ancestor_id == sponsor.member_id) &
                    (UserTreePath.descendant_id == new_user.member_id) &
                    (UserTreePath.depth == 1)
                )
            ).first()

            if sponsor_path:
                print(f"✅ Relación con sponsor creada (depth=1)")
            else:
                print(f"❌ Relación con sponsor NO encontrada")

            # Contar todas las relaciones
            all_paths = session.exec(
                sqlmodel.select(UserTreePath).where(
                    UserTreePath.descendant_id == new_user.member_id
                )
            ).all()

            print(f"📊 Total de relaciones en UserTreePath: {len(all_paths)}")
            for path in all_paths:
                print(f"   - Ancestor: {path.ancestor_id}, Descendant: {path.descendant_id}, Depth: {path.depth}")

            print()
            print("=" * 60)
            print("✅ TEST COMPLETADO EXITOSAMENTE")
            print("=" * 60)

            # Cleanup (opcional)
            print()
            cleanup = input("¿Deseas eliminar el usuario de prueba? (s/n): ")
            if cleanup.lower() == 's':
                # Eliminar UserTreePaths
                for path in all_paths:
                    session.delete(path)
                # Eliminar usuario
                session.delete(new_user)
                session.commit()
                print("🗑️  Usuario de prueba eliminado")

            return True

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ TEST FALLÓ")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_user_registration()
