"""
Servicio de gestión de órdenes.
Maneja queries a la base de datos y lógica de negocio para órdenes.
"""
from typing import List, Dict, Optional
from datetime import datetime, timezone
from decimal import Decimal
from sqlmodel import Session, select, and_, desc, asc
from database.orders import Orders, OrderStatus
from database.order_items import OrderItems
from database.products import Products
from database.addresses import Addresses
from database.users import Users
from database.engine_config import get_configured_engine
from NNProtect_new_website.utils.timezone_mx import convert_to_mexico_time


class OrderService:
    """
    Servicio para operaciones de órdenes.
    Implementa queries optimizadas con JOINs y formateo de datos.
    """

    @staticmethod
    def get_user_orders(member_id: int) -> List[Dict]:
        """
        Obtiene todas las órdenes de un usuario específico.

        Args:
            member_id: ID del miembro del usuario

        Returns:
            Lista de órdenes formateadas con información completa

        Performance:
        - Usa JOIN con addresses para obtener dirección en una sola query
        - Índices en member_id, status, created_at para búsqueda rápida
        """
        try:
            engine = get_configured_engine()
            with Session(engine) as session:
                # Query optimizada con JOIN
                statement = (
                    select(Orders, Addresses)
                    .outerjoin(Addresses, Orders.shipping_address_id == Addresses.id)
                    .where(Orders.member_id == member_id)
                    .order_by(desc(Orders.created_at))
                )

                results = session.exec(statement).all()

                orders = []
                for order, address in results:
                    # Formatear cada orden
                    formatted_order = OrderService._format_order(order, address)
                    orders.append(formatted_order)

                return orders

        except Exception as e:
            print(f"❌ Error obteniendo órdenes del usuario {member_id}: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def get_order_details(order_id: int) -> Optional[Dict]:
        """
        Obtiene los detalles completos de una orden específica.
        Incluye información de la orden, items y productos.

        Args:
            order_id: ID de la orden

        Returns:
            Dict con 'order' (datos de orden) e 'items' (lista de productos)
        """
        try:
            engine = get_configured_engine()
            with Session(engine) as session:
                # Obtener orden con dirección
                order_statement = (
                    select(Orders, Addresses)
                    .outerjoin(Addresses, Orders.shipping_address_id == Addresses.id)
                    .where(Orders.id == order_id)
                )

                order_result = session.exec(order_statement).first()

                if not order_result:
                    print(f"❌ Orden {order_id} no encontrada")
                    return None

                order, address = order_result

                # Obtener items de la orden con productos
                items_statement = (
                    select(OrderItems, Products)
                    .join(Products, OrderItems.product_id == Products.id)
                    .where(OrderItems.order_id == order_id)
                )

                items_results = session.exec(items_statement).all()

                # Formatear orden
                formatted_order = OrderService._format_order(order, address)

                # Formatear items
                formatted_items = []
                for order_item, product in items_results:
                    formatted_item = OrderService._format_order_item(order_item, product)
                    formatted_items.append(formatted_item)

                return {
                    "order": formatted_order,
                    "items": formatted_items
                }

        except Exception as e:
            print(f"❌ Error obteniendo detalles de orden {order_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def get_orders_by_status(member_id: int, status: str) -> List[Dict]:
        """
        Obtiene órdenes de un usuario filtradas por estado.

        Args:
            member_id: ID del miembro
            status: Estado de la orden (OrderStatus value)

        Returns:
            Lista de órdenes formateadas
        """
        try:
            engine = get_configured_engine()
            with Session(engine) as session:
                statement = (
                    select(Orders, Addresses)
                    .outerjoin(Addresses, Orders.shipping_address_id == Addresses.id)
                    .where(
                        and_(
                            Orders.member_id == member_id,
                            Orders.status == status
                        )
                    )
                    .order_by(desc(Orders.created_at))
                )

                results = session.exec(statement).all()

                orders = []
                for order, address in results:
                    formatted_order = OrderService._format_order(order, address)
                    orders.append(formatted_order)

                return orders

        except Exception as e:
            print(f"❌ Error obteniendo órdenes por estado: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def search_orders_by_number(member_id: int, search_query: str) -> List[Dict]:
        """
        Busca órdenes por número de orden (búsqueda parcial).

        Args:
            member_id: ID del miembro
            search_query: Texto a buscar en el ID de la orden

        Returns:
            Lista de órdenes que coinciden con la búsqueda
        """
        try:
            engine = get_configured_engine()
            with Session(engine) as session:
                # Buscar por ID que contenga la query
                statement = (
                    select(Orders, Addresses)
                    .outerjoin(Addresses, Orders.shipping_address_id == Addresses.id)
                    .where(Orders.member_id == member_id)
                    .order_by(desc(Orders.created_at))
                )

                results = session.exec(statement).all()

                # Filtrar en Python para búsqueda flexible
                orders = []
                search_lower = search_query.lower().strip()
                for order, address in results:
                    if search_lower in str(order.id).lower():
                        formatted_order = OrderService._format_order(order, address)
                        orders.append(formatted_order)

                return orders

        except Exception as e:
            print(f"❌ Error buscando órdenes: {e}")
            import traceback
            traceback.print_exc()
            return []

    # Métodos privados de formateo

    @staticmethod
    def _format_order(order: Orders, address: Optional[Addresses] = None) -> Dict:
        """
        Formatea una orden para el frontend.
        Convierte tipos de datos y añade información calculada.

        Args:
            order: Orden de la base de datos
            address: Dirección de envío (opcional)

        Returns:
            Dict con datos formateados para UI
        """
        # Formatear dirección
        if address:
            shipping_address = f"{address.street}, {address.neighborhood}, {address.city}, {address.state}, {address.country}"
            address_alias = f"{address.city}, {address.state}"
        else:
            shipping_address = "Sin dirección"
            address_alias = "No disponible"

        # Convertir timestamps a timezone México
        created_at_mx = convert_to_mexico_time(order.created_at) if order.created_at else None
        submitted_at_mx = convert_to_mexico_time(order.submitted_at) if order.submitted_at else None
        payment_confirmed_at_mx = convert_to_mexico_time(order.payment_confirmed_at) if order.payment_confirmed_at else None

        # Formatear fecha de compra (para display)
        purchase_date = created_at_mx.strftime("%d/%m/%Y") if created_at_mx else "N/A"

        # Determinar estado para UI con badge color
        status_display, badge_color = OrderService._get_status_display(order.status)

        # Determinar método de pago con icono
        payment_method, payment_icon = OrderService._get_payment_method_display(order.payment_method)

        return {
            "order_id": order.id,
            "order_number": f"#{order.id}",  # Formato display
            "member_id": order.member_id,
            "shipping_address": shipping_address,
            "address_alias": address_alias,
            "purchase_date": purchase_date,
            "payment_method": payment_method,
            "payment_icon": payment_icon,
            "total": float(order.total),
            "total_formatted": f"${order.total:,.2f}",
            "currency": order.currency,
            "status": status_display,
            "status_raw": order.status,
            "badge_color": badge_color,
            "total_pv": order.total_pv,
            "total_vn": float(order.total_vn),
            # Raw timestamps para sorting
            "created_at_raw": order.created_at,
            "submitted_at_raw": order.submitted_at,
            "payment_confirmed_at_raw": order.payment_confirmed_at,
            # Formatted timestamps
            "created_at_display": created_at_mx.strftime("%d/%m/%Y %H:%M") if created_at_mx else "N/A",
            "payment_confirmed_at_display": payment_confirmed_at_mx.strftime("%d/%m/%Y %H:%M") if payment_confirmed_at_mx else "N/A",
        }

    @staticmethod
    def _format_order_item(order_item: OrderItems, product: Products) -> Dict:
        """
        Formatea un item de orden para el frontend.

        Args:
            order_item: Item de la orden
            product: Producto asociado

        Returns:
            Dict con información del producto en la orden
        """
        return {
            "item_id": order_item.id,
            "product_id": order_item.product_id,
            "product_name": product.product_name,
            "quantity": order_item.quantity,
            "unit_price": float(order_item.unit_price),
            "unit_price_formatted": f"${order_item.unit_price:,.2f}",
            "line_total": float(order_item.line_total),
            "line_total_formatted": f"${order_item.line_total:,.2f}",
            "unit_pv": order_item.unit_pv,
            "unit_vn": float(order_item.unit_vn),
            "line_pv": order_item.line_pv,
            "line_vn": float(order_item.line_vn),
            "presentation": product.presentation,
            "type": product.type,
        }

    @staticmethod
    def _get_status_display(status: str) -> tuple[str, str]:
        """
        Mapea estados de BD a display del UI con color de badge.

        Returns:
            Tupla (estado_display, color_badge)
        """
        status_map = {
            OrderStatus.DRAFT.value: ("Borrador", "gray"),
            OrderStatus.PENDING_PAYMENT.value: ("Pendiente", "orange"),
            OrderStatus.PAYMENT_CONFIRMED.value: ("Pagado", "green"),
            OrderStatus.PROCESSING.value: ("En proceso", "blue"),
            OrderStatus.SHIPPED.value: ("Enviado", "cyan"),
            OrderStatus.DELIVERED.value: ("Entregado", "green"),
            OrderStatus.CANCELLED.value: ("Cancelado", "red"),
            OrderStatus.REFUNDED.value: ("Reembolsado", "red"),
        }

        return status_map.get(status, ("Desconocido", "gray"))

    @staticmethod
    def _get_payment_method_display(payment_method: Optional[str]) -> tuple[str, str]:
        """
        Mapea métodos de pago a display con icono.

        Returns:
            Tupla (método_display, icono)
        """
        if not payment_method:
            return ("No especificado", "help-circle")

        method_map = {
            "credit_card": ("Tarjeta crédito", "credit-card"),
            "debit_card": ("Tarjeta débito", "credit-card"),
            "paypal": ("PayPal", "wallet"),
            "stripe": ("Stripe", "credit-card"),
            "transfer": ("Transferencia", "banknote"),
            "wallet": ("Billetera digital", "wallet"),
        }

        # Buscar case-insensitive
        payment_lower = payment_method.lower()
        for key, value in method_map.items():
            if key in payment_lower:
                return value

        return (payment_method, "credit-card")

    @staticmethod
    def get_order_items_for_mobile(order_id: int) -> List[Dict]:
        """
        Obtiene items de una orden para vista móvil.
        Versión simplificada con solo los datos necesarios.

        Args:
            order_id: ID de la orden

        Returns:
            Lista de productos simplificados
        """
        try:
            engine = get_configured_engine()
            with Session(engine) as session:
                statement = (
                    select(OrderItems, Products)
                    .join(Products, OrderItems.product_id == Products.id)
                    .where(OrderItems.order_id == order_id)
                )

                results = session.exec(statement).all()

                items = []
                for order_item, product in results:
                    items.append({
                        "product_name": product.product_name,
                        "quantity": order_item.quantity,
                    })

                return items

        except Exception as e:
            print(f"❌ Error obteniendo items para móvil: {e}")
            import traceback
            traceback.print_exc()
            return []
