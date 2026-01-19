"""
Script para crear una orden de prueba completa.
Genera órdenes realistas con productos suplementos de forma interactiva.
Incluye todas las conexiones necesarias a tablas relacionadas.

Rol: Senior Backend Developer
Principios: KISS, DRY, POO
"""

import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reflex as rx
import sqlmodel
from datetime import datetime, timezone
from typing import Optional, List

from database.users import Users
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.products import Products
from database.periods import Periods
from NNProtect_new_website.modules.network.backend.commission_service import CommissionService
from NNProtect_new_website.modules.network.backend.genealogy_service import GenealogyService
from NNProtect_new_website.modules.network.backend.rank_service import RankService
from NNProtect_new_website.modules.network.backend.pv_update_service import PVUpdateService


class TestOrderGenerator:
    """
    Generador de órdenes de prueba.
    Principio POO: Encapsula la lógica de creación de órdenes.
    """

    @classmethod
    def create_supplement_order(cls, session, member_id: int, quantity_per_product: int = 1) -> Optional[int]:
        """
        Crea una orden completa con productos tipo 'supplement'.

        Proceso completo:
        1. Validar usuario existe
        2. Obtener período actual
        3. Seleccionar 5 productos suplementos
        4. Crear orden (status: DRAFT)
        5. Crear order_items con valores congelados
        6. Calcular totales de la orden
        7. Confirmar pago (PAYMENT_CONFIRMED)
        8. Disparar comisiones (Bono Rápido si aplica)
        9. Verificar actualización de rango

        Args:
            session: Sesión de base de datos
            member_id: ID del miembro que hace la compra
            quantity_per_product: Cantidad por producto (default: 1)

        Returns:
            ID de la orden creada o None si falla
        """
        try:
            print(f"\n🛒 Iniciando creación de orden para member_id={member_id}...")

            # 1. Validar que el usuario existe
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()

            if not user:
                print(f"❌ Usuario con member_id={member_id} no existe")
                return None

            print(f"✅ Usuario encontrado: {user.first_name} {user.last_name} ({user.country_cache})")

            # 2. Obtener período actual
            current_period = cls._get_current_period(session)
            period_id = current_period.id if current_period else None

            if not current_period:
                print("⚠️  No hay período activo, continuando sin período...")
            else:
                print(f"✅ Período actual: {current_period.name} (ID: {current_period.id})")

            # 3. Seleccionar 5 productos (excluyendo kits)
            supplements = session.exec(
                sqlmodel.select(Products)
                .where(
                    (Products.type != "kit") | (Products.type.is_(None))
                )
                .limit(5)
            ).all()

            if len(supplements) < 5:
                print(f"⚠️  Solo hay {len(supplements)} productos disponibles")

            if not supplements:
                print("❌ No hay productos en la base de datos")
                return None

            print(f"✅ Seleccionados {len(supplements)} productos:")
            for prod in supplements:
                print(f"   - {prod.product_name} (PV_MX: {prod.pv_mx}, VN_MX: {prod.vn_mx})")

            # 4. Crear orden inicial (DRAFT)
            order = Orders(
                member_id=member_id,
                country=user.country_cache or "Mexico",
                currency=cls._get_currency_for_country(user.country_cache or "Mexico"),
                subtotal=0.0,
                shipping_cost=0.0,
                total=0.0,
                total_pv=0,
                total_vn=0.0,
                status=OrderStatus.DRAFT.value,
                payment_confirmed_at=None,
                period_id=period_id,
                created_at=datetime.now(timezone.utc)
            )

            session.add(order)
            session.flush()  # Obtener order.id

            print(f"✅ Orden creada (ID: {order.id}) - Status: DRAFT")

            # 5. Crear order_items con valores congelados
            subtotal = 0.0
            total_pv = 0
            total_vn = 0.0

            for product in supplements:
                # Congelar precios al momento de agregar al carrito
                country = user.country_cache or "Mexico"
                unit_price = cls._get_price_for_country(product, country)
                unit_pv = cls._get_pv_for_country(product, country)
                unit_vn = cls._get_vn_for_country(product, country)

                # Crear item
                order_item = OrderItems(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity_per_product,
                    unit_price=unit_price,
                    unit_pv=unit_pv,
                    unit_vn=unit_vn,
                    line_total=0.0,
                    line_pv=0,
                    line_vn=0.0
                )

                # Calcular totales del item
                order_item.calculate_totals()

                session.add(order_item)

                # Acumular totales
                subtotal += order_item.line_total
                total_pv += order_item.line_pv
                total_vn += order_item.line_vn

                print(f"✅ Item agregado: {product.product_name} x{quantity_per_product} = ${order_item.line_total:.2f} ({order_item.line_pv} PV, {order_item.line_vn} VN)")

            session.flush()

            # 6. Calcular totales de la orden
            shipping_cost = cls._calculate_shipping(user.country_cache or "Mexico", subtotal)

            order.subtotal = subtotal
            order.shipping_cost = shipping_cost
            order.total = subtotal + shipping_cost
            order.total_pv = total_pv
            order.total_vn = total_vn

            session.add(order)
            session.flush()

            print(f"✅ Totales calculados:")
            print(f"   - Subtotal: ${order.subtotal:.2f}")
            print(f"   - Envío: ${order.shipping_cost:.2f}")
            print(f"   - Total: ${order.total:.2f}")
            print(f"   - PV Total: {order.total_pv}")
            print(f"   - VN Total: {order.total_vn:.2f}")

            # 7. Simular confirmación de pago (PAYMENT_CONFIRMED)
            order.status = OrderStatus.PAYMENT_CONFIRMED.value
            order.payment_confirmed_at = datetime.now(timezone.utc)

            session.add(order)
            session.commit()

            print(f"✅ Pago confirmado - Status: PAYMENT_CONFIRMED")

            # 8. Actualizar PV y rangos
            print("📊 Actualizando PV y rangos...")
            pv_updated = PVUpdateService.process_order_pv_update(session, order.id)

            if not pv_updated:
                print("⚠️  Advertencia: No se pudo actualizar PV")

            # 9. Disparar comisiones
            print("🎁 Procesando comisiones...")

            # Bono Rápido (solo si hay kits)
            fast_start_ids = CommissionService.process_fast_start_bonus(session, order.id)
            if fast_start_ids:
                print(f"✅ {len(fast_start_ids)} comisiones de Bono Rápido generadas")
            else:
                print("⚠️  No se generaron comisiones de Bono Rápido (solo suplementos)")

            session.commit()

            print(f"\n🎉 Orden completada exitosamente (ID: {order.id})")
            print(f"📋 Resumen:")
            print(f"   - Member ID: {member_id}")
            print(f"   - Productos: {len(supplements)}")
            print(f"   - Total: ${order.total:.2f} {order.currency}")
            print(f"   - PV: {order.total_pv}")
            print(f"   - VN: {order.total_vn:.2f}")
            print(f"   - Status: {order.status}")

            return order.id

        except Exception as e:
            session.rollback()
            print(f"❌ Error creando orden: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def _get_current_period(cls, session) -> Optional[Periods]:
        """Obtiene el período actual activo."""
        try:
            current_date = datetime.now(timezone.utc)

            current_period = session.exec(
                sqlmodel.select(Periods)
                .where(
                    Periods.starts_on <= current_date,
                    Periods.ends_on >= current_date,
                    Periods.closed_at.is_(None)
                )
            ).first()

            return current_period

        except Exception as e:
            print(f"⚠️  Error obteniendo período actual: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def _get_currency_for_country(cls, country: str) -> str:
        """Obtiene el código de moneda según el país."""
        currency_map = {
            "Mexico": "MXN",
            "USA": "USD",
            "Colombia": "COP"
        }
        return currency_map.get(country, "MXN")

    @classmethod
    def _get_price_for_country(cls, product: Products, country: str) -> float:
        """Obtiene el precio del producto según el país."""
        if country == "Mexico":
            return product.price_mx
        elif country == "USA":
            return product.price_usa
        elif country == "Colombia":
            return product.price_col
        else:
            return product.price_mx

    @classmethod
    def _get_pv_for_country(cls, product: Products, country: str) -> int:
        """Obtiene el PV del producto según el país."""
        if country == "Mexico":
            return product.pv_mx
        elif country == "USA":
            return product.pv_usa
        elif country == "Colombia":
            return product.pv_colombia
        else:
            return product.pv_mx

    @classmethod
    def _get_vn_for_country(cls, product: Products, country: str) -> float:
        """Obtiene el VN del producto según el país."""
        if country == "Mexico":
            return product.vn_mx
        elif country == "USA":
            return product.vn_usa
        elif country == "Colombia":
            return product.vn_colombia
        else:
            return product.vn_mx

    @classmethod
    def _calculate_shipping(cls, country: str, subtotal: float) -> float:
        """Calcula costo de envío según país y subtotal."""
        # Envío gratis para compras mayores a cierto monto
        free_shipping_threshold = {
            "Mexico": 1000.0,
            "USA": 50.0,
            "Colombia": 150000.0
        }

        shipping_cost = {
            "Mexico": 150.0,
            "USA": 10.0,
            "Colombia": 25000.0
        }

        threshold = free_shipping_threshold.get(country, 1000.0)
        cost = shipping_cost.get(country, 150.0)

        return 0.0 if subtotal >= threshold else cost


def get_member_ids() -> List[int]:
    """
    Solicita al usuario los member_ids de forma interactiva.
    Permite ingresar múltiples IDs separados por Enter.
    
    Returns:
        Lista de member_ids ingresados
    """
    print("\n" + "=" * 60)
    print("PASO 1: INGRESO DE MEMBER IDs")
    print("=" * 60)
    print("\nIngrese los member_id de los usuarios (uno por línea)")
    print("Presione Enter sin escribir nada para finalizar\n")
    
    member_ids = []
    
    while True:
        try:
            user_input = input(f"Member ID #{len(member_ids) + 1}: ").strip()
            
            # Si está vacío, terminar captura
            if not user_input:
                if len(member_ids) == 0:
                    print("⚠️  Debe ingresar al menos un member_id")
                    continue
                break
            
            # Validar que sea un número
            member_id = int(user_input)
            
            if member_id <= 0:
                print("❌ El member_id debe ser un número positivo")
                continue
            
            if member_id in member_ids:
                print(f"⚠️  El member_id {member_id} ya fue ingresado")
                continue
            
            member_ids.append(member_id)
            print(f"✅ Member ID {member_id} agregado")
            
        except ValueError:
            print("❌ Error: Debe ingresar un número válido")
        except KeyboardInterrupt:
            print("\n\n❌ Operación cancelada por el usuario")
            sys.exit(0)
    
    print(f"\n✅ Total de usuarios: {len(member_ids)}")
    print(f"📋 Member IDs: {', '.join(map(str, member_ids))}")
    
    return member_ids


def get_orders_per_user() -> int:
    """
    Solicita al usuario cuántas órdenes crear por cada member_id.
    
    Returns:
        Cantidad de órdenes a crear por usuario
    """
    print("\n" + "=" * 60)
    print("PASO 2: CANTIDAD DE ÓRDENES")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n¿Cuántas órdenes crear por cada usuario? (default: 1): ").strip()
            
            # Default a 1 si está vacío
            if not user_input:
                orders_count = 1
            else:
                orders_count = int(user_input)
            
            if orders_count <= 0:
                print("❌ La cantidad debe ser un número positivo")
                continue
            
            if orders_count > 10:
                confirm = input(f"⚠️  Va a crear {orders_count} órdenes por usuario. ¿Continuar? (s/n): ").strip().lower()
                if confirm not in ['s', 'si', 'y', 'yes']:
                    continue
            
            print(f"✅ Se crearán {orders_count} orden(es) por usuario")
            return orders_count
            
        except ValueError:
            print("❌ Error: Debe ingresar un número válido")
        except KeyboardInterrupt:
            print("\n\n❌ Operación cancelada por el usuario")
            sys.exit(0)


def confirm_execution(member_ids: List[int], orders_per_user: int) -> bool:
    """
    Muestra resumen y solicita confirmación antes de ejecutar.
    
    Args:
        member_ids: Lista de member_ids
        orders_per_user: Cantidad de órdenes por usuario
        
    Returns:
        True si el usuario confirma, False en caso contrario
    """
    total_orders = len(member_ids) * orders_per_user
    
    print("\n" + "=" * 60)
    print("CONFIRMACIÓN")
    print("=" * 60)
    print(f"\n📊 Resumen de la operación:")
    print(f"   - Usuarios: {len(member_ids)}")
    print(f"   - Órdenes por usuario: {orders_per_user}")
    print(f"   - Total de órdenes a crear: {total_orders}")
    print(f"\n📋 Member IDs: {', '.join(map(str, member_ids))}")
    
    while True:
        try:
            confirm = input("\n¿Desea continuar? (s/n): ").strip().lower()
            
            if confirm in ['s', 'si', 'y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                print("❌ Respuesta inválida. Ingrese 's' o 'n'")
                
        except KeyboardInterrupt:
            print("\n\n❌ Operación cancelada por el usuario")
            sys.exit(0)


def main():
    """Función principal para ejecutar el generador de órdenes de forma interactiva."""
    
    # Título principal
    print("\n" + "=" * 60)
    print("🚀 SCRIPT PARA CREAR NUEVA ORDEN")
    print("=" * 60)
    print("\nEste script creará órdenes de prueba con productos suplementos")
    print("para los member_ids especificados.\n")
    
    try:
        # Paso 1: Obtener member_ids
        member_ids = get_member_ids()
        
        # Paso 2: Obtener cantidad de órdenes por usuario
        orders_per_user = get_orders_per_user()
        
        # Paso 3: Confirmación
        if not confirm_execution(member_ids, orders_per_user):
            print("\n❌ Operación cancelada por el usuario")
            return
        
        # Paso 4: Ejecutar creación de órdenes
        print("\n" + "=" * 60)
        print("⚙️  PROCESANDO ÓRDENES")
        print("=" * 60)
        
        total_created = 0
        total_failed = 0
        
        with rx.session() as session:
            for member_id in member_ids:
                print(f"\n{'─' * 60}")
                print(f"📦 Procesando órdenes para Member ID: {member_id}")
                print(f"{'─' * 60}")
                
                for order_num in range(1, orders_per_user + 1):
                    print(f"\n🔄 Creando orden {order_num} de {orders_per_user}...")
                    
                    order_id = TestOrderGenerator.create_supplement_order(
                        session=session,
                        member_id=member_id,
                        quantity_per_product=1
                    )
                    
                    if order_id:
                        total_created += 1
                    else:
                        total_failed += 1
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL")
        print("=" * 60)
        print(f"\n✅ Órdenes creadas exitosamente: {total_created}")
        if total_failed > 0:
            print(f"❌ Órdenes fallidas: {total_failed}")
        print(f"\n🎉 Proceso completado")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()