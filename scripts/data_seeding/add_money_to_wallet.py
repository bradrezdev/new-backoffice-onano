"""
Script para añadir dinero a la billetera virtual de usuarios.
Útil para testing, bonificaciones especiales o ajustes administrativos.

Ejecutar: python testers/add_money_to_wallet.py
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import reflex as rx
from datetime import datetime, timezone

from database.users import Users
from database.wallet import Wallets, WalletTransactionType
from database.periods import Periods
from NNProtect_new_website.modules.finance.backend.wallet_service import WalletService


def print_header(title: str):
    """Imprime un header bonito"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def add_money_to_single_user(session, member_id: int, amount: float, currency: str, description: str) -> bool:
    """
    Añade dinero a la billetera de un usuario específico.

    Args:
        session: Sesión de base de datos
        member_id: ID del usuario
        amount: Monto a añadir
        currency: Moneda (MXN, USD, COP, DOP)
        description: Descripción del depósito

    Returns:
        True si se añadió exitosamente, False si falló
    """
    try:
        # Verificar que el usuario existe
        import sqlmodel
        user = session.exec(
            sqlmodel.select(Users).where(Users.member_id == member_id)
        ).first()

        if not user:
            print(f"❌ Usuario con member_id {member_id} no existe")
            return False

        # Verificar o crear wallet
        wallet = session.exec(
            sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
        ).first()

        if not wallet:
            # Crear wallet si no existe
            wallet_id = WalletService.create_wallet(session, member_id, currency)
            if not wallet_id:
                print(f"❌ No se pudo crear wallet para usuario {member_id}")
                return False
            print(f"✅ Wallet creada para usuario {member_id}")

        # Obtener balance anterior
        balance_before = WalletService.get_wallet_balance(session, member_id)

        # Crear transacción de ajuste de crédito
        import uuid
        from database.wallet import WalletTransactions, WalletTransactionStatus

        wallet = session.exec(
            sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
        ).first()

        balance_after = balance_before + amount

        transaction = WalletTransactions(
            transaction_uuid=str(uuid.uuid4()),
            member_id=member_id,
            transaction_type=WalletTransactionType.ADJUSTMENT_CREDIT.value,
            status=WalletTransactionStatus.COMPLETED.value,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            currency=currency,
            description=description,
            completed_at=datetime.now(timezone.utc)
        )

        session.add(transaction)

        # Actualizar balance de wallet
        wallet.balance = balance_after
        wallet.updated_at = datetime.now(timezone.utc)

        session.flush()

        print(f"✅ Usuario {member_id}: +{amount} {currency}")
        print(f"   Balance anterior: {balance_before} {currency}")
        print(f"   Balance nuevo: {balance_after} {currency}")

        return True

    except Exception as e:
        print(f"❌ Error añadiendo dinero a usuario {member_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_money_to_multiple_users(users_data: list) -> dict:
    """
    Añade dinero a múltiples usuarios en una sola transacción.

    Args:
        users_data: Lista de diccionarios con formato:
            [
                {"member_id": 1, "amount": 1000.0, "currency": "MXN", "description": "Bono especial"},
                {"member_id": 2, "amount": 500.0, "currency": "MXN", "description": "Ajuste administrativo"},
                ...
            ]

    Returns:
        Diccionario con resumen de resultados
    """
    print_header("AÑADIR DINERO A MÚLTIPLES USUARIOS")

    results = {
        "total": len(users_data),
        "success": 0,
        "failed": 0,
        "details": []
    }

    with rx.session() as session:
        for user_data in users_data:
            member_id = user_data.get("member_id")
            amount = user_data.get("amount", 0.0)
            currency = user_data.get("currency", "MXN")
            description = user_data.get("description", "Ajuste administrativo")

            print(f"\n📝 Procesando usuario {member_id}...")

            success = add_money_to_single_user(
                session=session,
                member_id=member_id,
                amount=amount,
                currency=currency,
                description=description
            )

            if success:
                results["success"] += 1
                results["details"].append({
                    "member_id": member_id,
                    "status": "success",
                    "amount": amount,
                    "currency": currency
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "member_id": member_id,
                    "status": "failed",
                    "amount": amount,
                    "currency": currency
                })

        # Commit todos los cambios si todo salió bien
        if results["failed"] == 0:
            session.commit()
            print("\n✅ Todos los cambios guardados exitosamente")
        else:
            print(f"\n⚠️  {results['failed']} operaciones fallaron")
            response = input("¿Desea guardar los cambios exitosos? (s/n): ")
            if response.lower() == 's':
                session.commit()
                print("✅ Cambios guardados")
            else:
                session.rollback()
                print("❌ Cambios revertidos")

    return results


def add_money_interactive():
    """Modo interactivo para añadir dinero a un usuario."""
    print_header("MODO INTERACTIVO - AÑADIR DINERO A WALLET")

    try:
        # Solicitar datos
        member_id = int(input("Ingrese member_id del usuario: "))
        amount = float(input("Ingrese monto a añadir: "))
        currency = input("Ingrese moneda (MXN/USD/COP/DOP) [default: MXN]: ").strip().upper() or "MXN"
        description = input("Ingrese descripción [default: Ajuste administrativo]: ").strip() or "Ajuste administrativo"

        print(f"\n📊 Resumen:")
        print(f"   Usuario: {member_id}")
        print(f"   Monto: {amount} {currency}")
        print(f"   Descripción: {description}")

        confirm = input("\n¿Confirmar operación? (s/n): ")

        if confirm.lower() != 's':
            print("❌ Operación cancelada")
            return

        # Ejecutar operación
        with rx.session() as session:
            success = add_money_to_single_user(
                session=session,
                member_id=member_id,
                amount=amount,
                currency=currency,
                description=description
            )

            if success:
                session.commit()
                print("\n✅ Operación completada exitosamente")

                # Mostrar balance final
                final_balance = WalletService.get_wallet_balance(session, member_id)
                print(f"\n💰 Balance final del usuario {member_id}: {final_balance} {currency}")
            else:
                session.rollback()
                print("\n❌ Operación fallida")

    except ValueError as e:
        print(f"❌ Error en los datos ingresados: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def add_money_batch_example():
    """Ejemplo de añadir dinero a múltiples usuarios en batch."""
    print_header("EJEMPLO BATCH - BONIFICACIÓN ESPECIAL")

    # Datos de ejemplo: bonificar primeros 3 usuarios con 1000 MXN cada uno
    users_data = [
        {
            "member_id": 1,
            "amount": 1000.0,
            "currency": "MXN",
            "description": "Bonificación especial - Octubre 2025"
        },
        {
            "member_id": 2,
            "amount": 500.0,
            "currency": "MXN",
            "description": "Bonificación especial - Octubre 2025"
        },
        {
            "member_id": 3,
            "amount": 750.0,
            "currency": "MXN",
            "description": "Bonificación especial - Octubre 2025"
        }
    ]

    print("📝 Se añadirá dinero a los siguientes usuarios:")
    for i, data in enumerate(users_data, 1):
        print(f"   {i}. Usuario {data['member_id']}: {data['amount']} {data['currency']}")

    confirm = input("\n¿Confirmar operación batch? (s/n): ")

    if confirm.lower() != 's':
        print("❌ Operación cancelada")
        return

    # Ejecutar batch
    results = add_money_to_multiple_users(users_data)

    # Mostrar resumen
    print_header("RESUMEN DE OPERACIÓN BATCH")
    print(f"✅ Exitosas: {results['success']}/{results['total']}")
    print(f"❌ Fallidas: {results['failed']}/{results['total']}")

    if results["failed"] > 0:
        print("\n⚠️  Operaciones fallidas:")
        for detail in results["details"]:
            if detail["status"] == "failed":
                print(f"   - Usuario {detail['member_id']}: {detail['amount']} {detail['currency']}")


def show_user_balance():
    """Consulta el balance actual de un usuario."""
    print_header("CONSULTAR BALANCE DE USUARIO")

    try:
        member_id = int(input("Ingrese member_id del usuario: "))

        with rx.session() as session:
            import sqlmodel
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()

            if not user:
                print(f"❌ Usuario con member_id {member_id} no existe")
                return

            wallet = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
            ).first()

            if not wallet:
                print(f"⚠️  Usuario {member_id} no tiene wallet creada")
                print(f"   Nombre: {user.first_name} {user.last_name}")
                return

            print(f"\n💰 Balance de {user.first_name} {user.last_name}")
            print(f"   Member ID: {member_id}")
            print(f"   Balance: {wallet.balance} {wallet.currency}")
            print(f"   Estado: {wallet.status}")
            print(f"   Última actualización: {wallet.updated_at}")

            # Mostrar últimas 5 transacciones
            print(f"\n📜 Últimas transacciones:")
            transactions = WalletService.get_transaction_history(session, member_id, limit=5)

            if not transactions:
                print("   (Sin transacciones)")
            else:
                for i, tx in enumerate(transactions, 1):
                    sign = "+" if tx.amount >= 0 else ""
                    print(f"   {i}. {tx.transaction_type}: {sign}{tx.amount} {tx.currency}")
                    print(f"      {tx.description}")
                    print(f"      Balance después: {tx.balance_after} {tx.currency}")
                    print()

    except ValueError as e:
        print(f"❌ Error: Ingrese un member_id válido")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main_menu():
    """Menú principal del script."""
    while True:
        print("\n" + "="*80)
        print("  GESTIÓN DE BILLETERA VIRTUAL - NN PROTECT")
        print("="*80)
        print("\n1. Añadir dinero a un usuario (modo interactivo)")
        print("2. Añadir dinero a múltiples usuarios (ejemplo batch)")
        print("3. Consultar balance de usuario")
        print("4. Salir")

        option = input("\nSeleccione una opción: ").strip()

        if option == "1":
            add_money_interactive()
        elif option == "2":
            add_money_batch_example()
        elif option == "3":
            show_user_balance()
        elif option == "4":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "SCRIPT DE GESTIÓN DE BILLETERA VIRTUAL" + " "*24 + "║")
    print("╚" + "="*78 + "╝")

    main_menu()
