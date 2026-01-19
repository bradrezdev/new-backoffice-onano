"""
Gestor de productos para la tienda NN Protect.
Maneja la lógica de negocio para obtener productos con precios según país.
"""
import reflex as rx
import time
from typing import List, Dict, Optional
from database.products import Products
from database.addresses import Countries

from ...auth.auth_state import UserDataManager

class ProductManager:
    """
    Clase para gestionar la lógica de productos en la tienda.
    Sigue principios POO para encapsular operaciones de productos.
    """

    @staticmethod
    def _map_country_string_to_enum(country_str: str) -> Optional[Countries]:
        """
        Mapea string de país a enum Countries.
        Principio KISS: mapeo directo y simple.
        
        Args:
            country_str: String del país (ej: "MEXICO", "USA")
            
        Returns:
            Countries: Enum correspondiente o None si no existe
        """
        if not country_str:
            return None
        
        mapping = {
            "MEXICO": Countries.MEXICO,
            "USA": Countries.USA,
            "COLOMBIA": Countries.COLOMBIA,
            "PUERTO_RICO": Countries.PUERTO_RICO,
        }
        return mapping.get(country_str.upper())

    @staticmethod
    def get_all_products(limit: Optional[int] = None, offset: Optional[int] = None) -> List[Products]:
        """
        Obtiene todos los productos de la base de datos con paginación opcional.
        
        Args:
            limit: Número máximo de registros a retornar
            offset: Número de registros a saltar
            
        Returns:
            List[Products]: Lista de productos
        """
        try:
            with rx.session() as session:
                from sqlmodel import select
                statement = select(Products)
                
                # Aplicar ordenamiento por defecto para consistencia en paginación
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
        """
        Obtiene un producto específico por su ID.
        Principio KISS: consulta simple y directa.
        
        Args:
            product_id: ID del producto a buscar
            
        Returns:
            Products: Objeto producto o None si no existe
        """
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
    def get_product_price_by_country(product: Products, country: Countries) -> Optional[float]:
        """
        Obtiene el precio de un producto dado un país (Enum).
        Optimizado para evitar consultas a BD.
        """
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
        """
        Obtiene el precio de un producto según el país de registro del usuario.
        Aplica principio KISS: lógica simple y directa.
        
        Args:
            product: Objeto producto
            user_id: ID del usuario para determinar su país
            
        Returns:
            float: Precio del producto en la moneda del país, None si no existe
        """
        
        country_str = UserDataManager.get_user_country_by_id(user_id)
        if not country_str:
            return None
        
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
        """
        Obtiene los puntos de valor (PV) de un producto según el país del usuario.
        
        Args:
            product: Objeto producto
            user_id: ID del usuario
            
        Returns:
            int: Puntos de valor del producto
        """
        
        country_str = UserDataManager.get_user_country_by_id(user_id)
        if not country_str:
            return 0
        
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
    def get_product_vn_by_user(product: Products, user_id: int) -> Optional[float]:
        """
        Obtiene el valor neto (VN) de un producto según el país del usuario.
        
        Args:
            product: Objeto producto
            user_id: ID del usuario
            
        Returns:
            float: Valor neto del producto, None si no existe
        """
        
        country_str = UserDataManager.get_user_country_by_id(user_id)
        if not country_str:
            return None
        
        country = ProductManager._map_country_string_to_enum(country_str)
        return ProductManager.get_product_vn_by_country(product, country)

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
        """
        Obtiene el símbolo de moneda según el país del usuario.
        Principio DRY: centralizamos la lógica de monedas.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            str: Símbolo de la moneda
        """
        
        country_str = UserDataManager.get_user_country_by_id(user_id)
        if not country_str:
            return "$"
        
        country = ProductManager._map_country_string_to_enum(country_str)
        return ProductManager.get_currency_symbol_by_country(country)

    @staticmethod
    def format_product_data_for_store(products: List[Products], user_id: int) -> List[Dict]:
        """
        Formatea los datos de productos para usar en la tienda.
        Aplica principio YAGNI: solo los datos necesarios para la tienda.
        🚀 OPTIMIZADO: Elimina problema N+1 cargando país UNA sola vez.
        
        Args:
            products: Lista de productos
            user_id: ID del usuario para determinar precios y moneda
            
        Returns:
            List[Dict]: Lista de productos formateados para la tienda
        """

        start_time = time.time()
        
        formatted_products = []
        
        # 🚀 OPTIMIZACIÓN: Cargar país y enum UNA sola vez fuera del bucle
        # Esto reduce N consultas a BD (donde N = num productos) a 1 consulta.
        country_str = UserDataManager.get_user_country_by_id(user_id)
        country_enum = ProductManager._map_country_string_to_enum(country_str)
        
        # Pre-calcular el símbolo de moneda
        currency = ProductManager.get_currency_symbol_by_country(country_enum)
        
        for product in products:
            # Usar métodos optimizados que no hacen queries
            price = ProductManager.get_product_price_by_country(product, country_enum)
            pv = ProductManager.get_product_pv_by_country(product, country_enum)
            vn = ProductManager.get_product_vn_by_country(product, country_enum)
            
            # Solo incluir productos que tengan precio definido
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
                    "is_new": product.is_new,  # ✅ Incluir flag para filtrar en memoria
                })
        
        total_time = time.time() - start_time
        print(f"⚡ format_product_data_for_store: {len(products)} productos procesados en {total_time:.4f}s")
        return formatted_products

    @staticmethod
    def get_latest_products() -> List[Products]:
        """
        Obtiene productos marcados como nuevos (is_new = True).
        Principio KISS: consulta simple y directa.
        
        Returns:
            List[Products]: Lista de productos nuevos
        """
        try:
            with rx.session() as session:
                from sqlmodel import select
                statement = select(Products).where(Products.is_new == True)
                latest_products = session.exec(statement).all()
                return list(latest_products)
        except Exception as e:
            print(f"❌ Error obteniendo productos nuevos: {e}")
            return []

    @staticmethod
    def get_popular_products(limit: int = 5) -> List[Products]:
        """
        Obtiene los productos más populares basados en OrderItems confirmados.
        Principio DRY: calcula dinámicamente desde Orders + OrderItems.

        Args:
            limit: Número máximo de productos a retornar (default: 5)

        Returns:
            List[Products]: Lista de productos más comprados
        """
        try:
            with rx.session() as session:
                from sqlmodel import select, func
                from database.orders import Orders, OrderStatus
                from database.order_items import OrderItems

                # Subconsulta: contar cuántas veces se compró cada producto
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

                # Join con productos y ordenar por popularidad
                statement = (
                    select(Products)
                    .join(subquery, Products.id == subquery.c.product_id)
                    .order_by(subquery.c.total_purchased.desc())
                    .limit(limit)
                )

                popular_products = session.exec(statement).all()
                return list(popular_products)

        except Exception as e:
            print(f"❌ Error obteniendo productos populares: {e}")
            return []

    @staticmethod
    def get_latest_products_formatted(user_id: int) -> List[Dict]:
        """
        Obtiene productos nuevos formateados para la tienda.
        Principio DRY: reutiliza format_product_data_for_store.
        
        Args:
            user_id: ID del usuario para precios correctos
            
        Returns:
            List[Dict]: Lista de productos nuevos formateados
        """
        latest_products = ProductManager.get_latest_products()
        return ProductManager.format_product_data_for_store(latest_products, user_id)

    @staticmethod
    def get_popular_products_formatted(user_id: int, limit: int = 5) -> List[Dict]:
        """
        Obtiene productos populares formateados para la tienda.
        Principio DRY: reutiliza format_product_data_for_store.
        
        Args:
            user_id: ID del usuario para precios correctos
            limit: Número máximo de productos a retornar
            
        Returns:
            List[Dict]: Lista de productos populares formateados
        """
        popular_products = ProductManager.get_popular_products(limit)
        return ProductManager.format_product_data_for_store(popular_products, user_id)

    @staticmethod
    def get_products_by_type(product_type: str) -> List[Products]:
        """
        Obtiene productos filtrados por tipo específico.
        Principio KISS: consulta simple y directa por tipo.
        
        Args:
            product_type: Tipo de producto ("kit de inicio", "suplemento", "skincare", "desinfectante")
            
        Returns:
            List[Products]: Lista de productos del tipo especificado
        """
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
    def get_kit_inicio_products() -> List[Products]:
        """
        Obtiene productos del tipo "kit de inicio".
        Método específico para kits de inicio.
        
        Returns:
            List[Products]: Lista de kits de inicio
        """
        return ProductManager.get_products_by_type("kit de inicio")

    @staticmethod
    def get_supplement_products() -> List[Products]:
        """
        Obtiene productos del tipo "suplemento".
        Método específico para suplementos nutricionales.
        
        Returns:
            List[Products]: Lista de suplementos
        """
        return ProductManager.get_products_by_type("suplemento")

    @staticmethod
    def get_skincare_products() -> List[Products]:
        """
        Obtiene productos del tipo "skincare".
        Método específico para productos de cuidado de la piel.
        
        Returns:
            List[Products]: Lista de productos skincare
        """
        return ProductManager.get_products_by_type("skincare")

    @staticmethod
    def get_sanitize_products() -> List[Products]:
        """
        Obtiene productos del tipo "desinfectante".
        Método específico para productos desinfectantes.
        
        Returns:
            List[Products]: Lista de productos desinfectantes
        """
        return ProductManager.get_products_by_type("desinfectante")

    @staticmethod
    def get_kit_inicio_products_formatted(user_id: int) -> List[Dict]:
        """
        Obtiene kits de inicio formateados para la tienda.
        Principio DRY: reutiliza format_product_data_for_store.
        
        Args:
            user_id: ID del usuario para precios correctos
            
        Returns:
            List[Dict]: Lista de kits de inicio formateados
        """
        kit_products = ProductManager.get_kit_inicio_products()
        return ProductManager.format_product_data_for_store(kit_products, user_id)

    @staticmethod
    def get_supplement_products_formatted(user_id: int) -> List[Dict]:
        """
        Obtiene suplementos formateados para la tienda.
        Principio DRY: reutiliza format_product_data_for_store.
        
        Args:
            user_id: ID del usuario para precios correctos
            
        Returns:
            List[Dict]: Lista de suplementos formateados
        """
        supplement_products = ProductManager.get_supplement_products()
        return ProductManager.format_product_data_for_store(supplement_products, user_id)

    @staticmethod
    def get_skincare_products_formatted(user_id: int) -> List[Dict]:
        """
        Obtiene productos skincare formateados para la tienda.
        Principio DRY: reutiliza format_product_data_for_store.
        
        Args:
            user_id: ID del usuario para precios correctos
            
        Returns:
            List[Dict]: Lista de productos skincare formateados
        """
        skincare_products = ProductManager.get_skincare_products()
        return ProductManager.format_product_data_for_store(skincare_products, user_id)

    @staticmethod
    def get_sanitize_products_formatted(user_id: int) -> List[Dict]:
        """
        Obtiene productos desinfectantes formateados para la tienda.
        Principio DRY: reutiliza format_product_data_for_store.
        
        Args:
            user_id: ID del usuario para precios correctos
            
        Returns:
            List[Dict]: Lista de productos desinfectantes formateados
        """
        sanitize_products = ProductManager.get_sanitize_products()
        return ProductManager.format_product_data_for_store(sanitize_products, user_id)
    

class ProductDataService:
    """
    Servicio que proporciona acceso a datos de productos.
    Sigue principio de responsabilidad única (POO).
    """
    
    @staticmethod
    def get_products_for_store(user_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict]:
        """
        Obtiene productos formateados para mostrar en la tienda con soporte de paginación.
        Principio DRY: reutiliza ProductManager.
        
        Args:
            user_id: ID del usuario autenticado
            limit: Límite de productos
            offset: Desplazamiento
            
        Returns:
            List[Dict]: Productos formateados para la tienda
        """
        products = ProductManager.get_all_products(limit=limit, offset=offset)
        return ProductManager.format_product_data_for_store(products, user_id)
    
    @staticmethod
    def get_products_by_type(user_id: int, product_type: str) -> List[Dict]:
        """
        Obtiene productos filtrados por tipo.
        Principio YAGNI: solo filtrado básico por tipo.
        
        Args:
            user_id: ID del usuario
            product_type: Tipo de producto (suplemento, skincare, etc.)
            
        Returns:
            List[Dict]: Productos filtrados y formateados
        """
        all_products = ProductDataService.get_products_for_store(user_id)
        return [p for p in all_products if p["type"] == product_type]
    
    @staticmethod
    def get_product_by_id(product_id: int, user_id: int) -> Optional[Dict]:
        """
        Obtiene un producto específico por ID.
        
        Args:
            product_id: ID del producto
            user_id: ID del usuario
            
        Returns:
            Dict: Datos del producto formateados, None si no existe
        """
        all_products = ProductDataService.get_products_for_store(user_id)
        for product in all_products:
            if product["id"] == product_id:
                return product
        return None