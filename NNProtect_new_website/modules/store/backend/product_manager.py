"""
Gestor de productos para la tienda NN Protect.
Maneja la lógica de negocio para obtener productos con precios según país.
"""
import reflex as rx
import time
from typing import List, Dict, Optional
from database.products import Products
from database.addresses import Countries

from NNProtect_new_website.modules.auth.backend.user_data_service import UserDataService

class ProductManager:
    """
    Clase para gestionar la lógica de productos en la tienda.
    Sigue principios POO para encapsular operaciones de productos.
    """

    @staticmethod
    def _map_country_string_to_enum(country_str: str) -> Optional[Countries]:
        """
        Mapea string de país a enum Countries.
        Principio KISS: mapeo directo y simple con dict.
        """
        if not country_str:
            return None
        
        # Mapeo estático simple
        MAPPING = {
            "MEXICO": Countries.MEXICO,
            "USA": Countries.USA,
            "COLOMBIA": Countries.COLOMBIA,
            "PUERTO_RICO": Countries.PUERTO_RICO,
        }
        return MAPPING.get(country_str.upper())

    @staticmethod
    def get_all_products(limit: Optional[int] = None, offset: Optional[int] = None) -> List[Products]:
        """Obtiene todos los productos de la base de datos con paginación opcional."""
        try:
            with rx.session() as session:
                from sqlmodel import select
                statement = select(Products)
                
                if hasattr(Products, 'id'):
                    statement = statement.order_by(Products.id)
                
                if offset is not None:
                    statement = statement.offset(offset)
                if limit is not None:
                    statement = statement.limit(limit)
                    
                products = session.exec(statement).all()
                return list(products)
        except Exception as e:
            print(f"❌ Error obteniendo productos: {e}")
            return []

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Products]:
        """Obtiene un producto específico por su ID."""
        try:
            with rx.session() as session:
                from sqlmodel import select
                statement = select(Products).where(Products.id == product_id)
                product = session.exec(statement).first()
                return product
        except Exception as e:
            print(f"❌ Error obteniendo producto {product_id}: {e}")
            return None
    
    @staticmethod
    def get_products_by_type(product_type: str) -> List[Products]:
        """Obtiene productos filtrados por tipo específico."""
        try:
            with rx.session() as session:
                from sqlmodel import select
                statement = select(Products).where(Products.type == product_type)
                products = session.exec(statement).all()
                return list(products)
        except Exception as e:
            print(f"❌ Error obteniendo productos tipo '{product_type}': {e}")
            return []

    @staticmethod
    def get_product_price_by_country(product: Products, country: Countries) -> Optional[float]:
        """Obtiene el precio de un producto dado un país (Enum)."""
        if not country:
            return None
            
        if country == Countries.MEXICO:
            return product.price_mx
        elif country == Countries.USA:
            return product.price_usa
        elif country == Countries.COLOMBIA:
            return product.price_colombia
        else:
            return None

    @staticmethod
    def get_product_price_by_user(product: Products, user_id: int) -> Optional[float]:
        """Obtiene el precio de un producto según el país de registro del usuario."""
        country_str = UserDataService.get_user_country_by_id(user_id)
        country = ProductManager._map_country_string_to_enum(country_str)
        return ProductManager.get_product_price_by_country(product, country)

    @staticmethod
    def get_product_pv_by_country(product: Products, country: Countries) -> int:
        """Obtiene PV dado un país (Enum)."""
        if not country:
            return 0
        if country == Countries.MEXICO:
            return product.pv_mx
        elif country == Countries.USA:
            return product.pv_usa
        elif country == Countries.COLOMBIA:
            return product.pv_colombia
        return 0

    @staticmethod
    def get_product_pv_by_user(product: Products, user_id: int) -> int:
        """Obtiene PV según el país del usuario."""
        country_str = UserDataService.get_user_country_by_id(user_id)
        country = ProductManager._map_country_string_to_enum(country_str)
        return ProductManager.get_product_pv_by_country(product, country)

    @staticmethod
    def get_product_vn_by_country(product: Products, country: Countries) -> Optional[float]:
        """Obtiene VN dado un país (Enum)."""
        if not country:
            return None
        if country == Countries.MEXICO:
            return product.vn_mx
        elif country == Countries.USA:
            return product.vn_usa
        elif country == Countries.COLOMBIA:
            return product.vn_colombia
        return None

    @staticmethod
    def get_currency_symbol_by_country(country: Countries) -> str:
        """Obtiene símbolo de moneda dado un país (Enum)."""
        if not country:
            return "$"
        if country == Countries.MEXICO:
            return "MX$"
        elif country == Countries.USA:
            return "$"
        elif country == Countries.COLOMBIA:
            return "COP$"
        return "$"
    
    @staticmethod
    def get_currency_symbol_by_user(user_id: int) -> str:
        """Obtiene el símbolo de moneda según el país del usuario."""
        country_str = UserDataService.get_user_country_by_id(user_id)
        country = ProductManager._map_country_string_to_enum(country_str)
        return ProductManager.get_currency_symbol_by_country(country)

    @staticmethod
    def format_product_data_for_store(products: List[Products], user_id: int) -> List[Dict]:
        """
        Formatea los datos de productos para usar en la tienda.
        🚀 OPTIMIZADO: Carga país UNA sola vez fuera del loop.
        """
        start_time = time.time()
        formatted_products = []
        
        country_str = UserDataService.get_user_country_by_id(user_id)
        country_enum = ProductManager._map_country_string_to_enum(country_str)
        currency = ProductManager.get_currency_symbol_by_country(country_enum)
        
        for product in products:
            price = ProductManager.get_product_price_by_country(product, country_enum)
            pv = ProductManager.get_product_pv_by_country(product, country_enum)
            vn = ProductManager.get_product_vn_by_country(product, country_enum)
            
            if price is not None:
                formatted_products.append({
                    "id": product.id,
                    "name": product.product_name,
                    "type": product.type,
                    "presentation": product.presentation,
                    "description": product.description or "",
                    "price": price,
                    "pv": pv,
                    "vn": vn,
                    "currency": currency,
                    "formatted_price": f"{currency}{price:.2f}",
                    "is_new": product.is_new,
                })
        
        # print(f"⚡ Formatted {len(products)} products in {time.time() - start_time:.4f}s")
        return formatted_products

    # --- MÉTODOS UNIFICADOS (ELIMINADA GRASA TÉCNICA) ---

    @staticmethod
    def get_all_products_formatted(user_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict]:
        """Obtiene TODOS los productos formateados (Reemplaza a ProductDataService.get_products_for_store)."""
        products = ProductManager.get_all_products(limit=limit, offset=offset)
        return ProductManager.format_product_data_for_store(products, user_id)

    @staticmethod
    def get_products_by_type_formatted(user_id: int, product_type: str) -> List[Dict]:
        """
        Obtiene productos filtrados por tipo y formateados.
        Unifica todos los get_X_products_formatted.
        """
        products = ProductManager.get_products_by_type(product_type)
        return ProductManager.format_product_data_for_store(products, user_id)
    
    @staticmethod
    def get_product_by_id_formatted(user_id: int, product_id: int) -> Optional[Dict]:
        """Obtiene UN producto formateado eficientemente."""
        product = ProductManager.get_product_by_id(product_id)
        if not product:
            return None
        # Reutilizamos la lógica eficiente pasando una lista de un elemento
        formatted_list = ProductManager.format_product_data_for_store([product], user_id)
        return formatted_list[0] if formatted_list else None

    @staticmethod
    def get_latest_products_formatted(user_id: int) -> List[Dict]:
        """Obtiene productos nuevos formateados."""
        try:
            with rx.session() as session:
                from sqlmodel import select
                statement = select(Products).where(Products.is_new == True)
                products = session.exec(statement).all()
                return ProductManager.format_product_data_for_store(list(products), user_id)
        except Exception:
            return []

    @staticmethod
    def get_popular_products_formatted(user_id: int, limit: int = 5) -> List[Dict]:
        """Obtiene productos populares formateados."""
        try:
            with rx.session() as session:
                from sqlmodel import select, func
                from database.orders import Orders, OrderStatus
                from database.order_items import OrderItems

                subquery = (
                    select(
                        OrderItems.product_id,
                        func.sum(OrderItems.quantity).label('total_purchased')
                    )
                    .join(Orders, OrderItems.order_id == Orders.id)
                    .where(Orders.status == OrderStatus.PAYMENT_CONFIRMED.value)
                    .group_by(OrderItems.product_id)
                    .subquery()
                )

                statement = (
                    select(Products)
                    .join(subquery, Products.id == subquery.c.product_id)
                    .order_by(subquery.c.total_purchased.desc())
                    .limit(limit)
                )

                products = session.exec(statement).all()
                return ProductManager.format_product_data_for_store(list(products), user_id)
        except Exception:
            return []
