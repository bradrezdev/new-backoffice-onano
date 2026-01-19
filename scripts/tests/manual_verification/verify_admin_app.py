"""
Script para verificar que Admin App está correctamente integrado.
Verifica imports, tablas de base de datos y funcionalidad básica.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Verifica que todos los módulos del Admin App se importan correctamente."""
    print("\n" + "="*60)
    print("🔍 VERIFICANDO IMPORTS DEL ADMIN APP")
    print("="*60)

    try:
        from NNProtect_new_website.Admin_app import theme
        print("✅ theme.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando theme.py: {e}")
        return False

    try:
        from NNProtect_new_website.Admin_app import components
        print("✅ components.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando components.py: {e}")
        return False

    try:
        from NNProtect_new_website.Admin_app import admin_state
        print("✅ admin_state.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando admin_state.py: {e}")
        return False

    try:
        from NNProtect_new_website.Admin_app.admin_page import admin_page
        print("✅ admin_page.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando admin_page.py: {e}")
        return False

    return True

def test_database_tables():
    """Verifica que las tablas necesarias existen en la base de datos."""
    print("\n" + "="*60)
    print("🗄️  VERIFICANDO TABLAS DE BASE DE DATOS")
    print("="*60)

    try:
        import reflex as rx
        from sqlmodel import select
        from database import Users, UserProfiles, Addresses, Wallets, Products, Orders

        with rx.session() as session:
            # Verificar tabla Users
            users_count = session.exec(select(Users)).all()
            print(f"✅ Tabla 'users' existe ({len(users_count)} usuarios)")

            # Verificar tabla UserProfiles
            profiles_count = session.exec(select(UserProfiles)).all()
            print(f"✅ Tabla 'userprofiles' existe ({len(profiles_count)} perfiles)")

            # Verificar tabla Addresses
            addresses_count = session.exec(select(Addresses)).all()
            print(f"✅ Tabla 'addresses' existe ({len(addresses_count)} direcciones)")

            # Verificar tabla Wallets
            wallets_count = session.exec(select(Wallets)).all()
            print(f"✅ Tabla 'wallets' existe ({len(wallets_count)} billeteras)")

            # Verificar tabla Products
            products_count = session.exec(select(Products)).all()
            print(f"✅ Tabla 'products' existe ({len(products_count)} productos)")

            # Verificar tabla Orders
            orders_count = session.exec(select(Orders)).all()
            print(f"✅ Tabla 'orders' existe ({len(orders_count)} órdenes)")

            return True

    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

def test_services():
    """Verifica que los servicios necesarios están disponibles."""
    print("\n" + "="*60)
    print("🔧 VERIFICANDO SERVICIOS")
    print("="*60)

    try:
        from NNProtect_new_website.modules.finance.backend.wallet_service import WalletService
        print("✅ WalletService disponible")
    except Exception as e:
        print(f"❌ Error importando WalletService: {e}")
        return False

    try:
        from NNProtect_new_website.modules.network.backend.loyalty_service import LoyaltyService
        print("✅ LoyaltyService disponible")
    except Exception as e:
        print(f"❌ Error importando LoyaltyService: {e}")
        return False

    try:
        from NNProtect_new_website.modules.finance.backend.exchange_service import ExchangeService
        print("✅ ExchangeService disponible")
    except Exception as e:
        print(f"❌ Error importando ExchangeService: {e}")
        return False

    return True

def main():
    """Función principal."""
    print("\n" + "="*60)
    print("🚀 VERIFICACIÓN DE INTEGRACIÓN - ADMIN APP")
    print("="*60)

    results = {
        "imports": test_imports(),
        "database": test_database_tables(),
        "services": test_services()
    }

    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name.upper()}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 ¡Todas las verificaciones pasaron exitosamente!")
        print("\n📍 Puedes acceder al Admin App en: http://localhost:3000/admin")
        print("\n✨ Funcionalidades disponibles:")
        print("   1. Crear Cuenta sin Sponsor")
        print("   2. Crear Usuarios de Prueba")
        print("   3. Crear Órdenes")
        print("   4. Crear Red Descendente")
        print("   5. Agregar Dinero a Billetera")
        print("   6. Agregar Puntos de Lealtad")
    else:
        print("\n⚠️  Algunas verificaciones fallaron. Revisa los errores arriba.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
