"""
Estado para la tienda de productos NN Protect.
Maneja la carga y visualización de productos con precios por país.
"""
import reflex as rx
from typing import List, Dict, Optional, Any
from database.addresses import Countries
from .product_data.product_data_service import ProductDataService
from ..auth_service.auth_state import UserDataManager
from .product_manager import ProductManager

class CountProducts(rx.State):
    """
    Contador individual por producto y sistema de carrito.
    Principio KISS: variables simples y claras.
    """
    
    # ✅ Optimización: Usar un dict en lugar de 24 variables individuales
    counts: Dict[int, int] = {}
    
    # Sistema de carrito - Principio KISS: variables simples y claras
    cart_total: int = 0
    cart_items: Dict[str, int] = {}  # Keys son strings: str(product_id)
    
    # User ID para obtener precios correctos por país
    user_id: int = 1  # Por defecto usuario de prueba

    @rx.event
    def increment(self, product_id: int):
        """Incrementa contador específico usando dict"""
        current = self.counts.get(product_id, 0)
        self.counts[product_id] = current + 1
    
    @rx.event  
    def decrement(self, product_id: int):
        """Decrementa contador específico usando dict"""
        current = self.counts.get(product_id, 0)
        if current > 0:
            self.counts[product_id] = current - 1

    @rx.var
    def get_count_reactive(self) -> dict:
        """
        Método reactivo que devuelve un diccionario con todos los contadores.
        Principio DRY: un solo método para acceder a todos los contadores de forma reactiva.
        """
        return {str(k): v for k, v in self.counts.items()}

    @rx.event
    def add_to_cart(self, product_id: int):
        """
        Añade la cantidad actual del contador del producto al carrito.
        Principio KISS: operación simple y directa.
        """
        current_count = self.counts.get(product_id, 0)
        
        if current_count == 0:
            return
            
        # Verificar límite máximo de 20 productos en total
        if self.cart_total + current_count > 20:
            remaining_space = 20 - self.cart_total
            if remaining_space > 0:
                # Añadir solo lo que cabe
                self.cart_items[str(product_id)] = self.cart_items.get(str(product_id), 0) + remaining_space
                self.cart_total += remaining_space
            return
        
        # Añadir productos al carrito
        self.cart_items[str(product_id)] = self.cart_items.get(str(product_id), 0) + current_count
        self.cart_total += current_count
        
        # Resetear contador del producto después de añadir
        self.counts[product_id] = 0

    @rx.event 
    def clear_cart(self):
        """
        Vacía completamente el carrito.
        Principio YAGNI: implementación simple para funcionalidad básica.
        """
        self.cart_total = 0
        self.cart_items = {}

    @rx.var(cache=True, auto_deps=False)
    def cart_items_detailed(self) -> List[Dict[str, Any]]:
        """
        Propiedad computada que devuelve los productos del carrito con información completa.
        Principio DRY: un solo lugar para obtener datos completos del carrito.
        """
        if not self.cart_items:
            return []
            
        from .product_manager import ProductManager
        
        cart_items = []
        
        for product_id_str, quantity in self.cart_items.items():
            product_id = int(product_id_str)
            
            # Obtener información del producto
            product = ProductManager.get_product_by_id(product_id)
            if not product:
                continue
                
            # Obtener precio y puntos según país del usuario
            price = ProductManager.get_product_price_by_user(product, self.user_id)
            volume_points = ProductManager.get_product_pv_by_user(product, self.user_id)
            
            if price is None:
                continue
                
            # Calcular subtotales
            subtotal = price * quantity
            volume_subtotal = volume_points * quantity
            
            # Construir objeto de producto para el carrito
            cart_item = {
                "id": product_id,
                "name": product.product_name,
                "price": price,
                "quantity": quantity,
                "volume_points": volume_points,
                "image": f"/product_{product_id}.jpg",
                "subtotal": subtotal,
                "volume_subtotal": volume_subtotal
            }
            cart_items.append(cart_item)
            
        return cart_items

    @rx.var
    def cart_subtotal(self) -> float:
        """Subtotal de productos en el carrito"""
        return sum(item["subtotal"] for item in self.cart_items_detailed)

    @rx.var
    def cart_volume_points(self) -> int:
        """Total de puntos de volumen en el carrito"""
        return sum(item["volume_subtotal"] for item in self.cart_items_detailed)

    @rx.var
    def cart_shipping_cost(self) -> float:
        """
        Costo de envío basado en el método seleccionado.
        TEMPORALMENTE: Solo recolección disponible (costo = 0.00)
        """
        return 0.00  # Recolección gratis - Envío a domicilio deshabilitado temporalmente

    @rx.var
    def cart_final_total(self) -> float:
        """Total final del carrito incluyendo envío"""
        return self.cart_subtotal + self.cart_shipping_cost

    @rx.event
    def increment_cart_item(self, product_id: int):
        """Incrementa cantidad de un producto específico en el carrito"""
        key = str(product_id)
        
        if key in self.cart_items and self.cart_total < 20:
            self.cart_items[key] += 1
            self.cart_total += 1
        elif key not in self.cart_items:
            pass
        elif self.cart_total >= 20:
            pass
    
    @rx.event
    def decrement_cart_item(self, product_id: int):
        """Decrementa cantidad de un producto específico en el carrito"""
        key = str(product_id)
        
        if key in self.cart_items and self.cart_items[key] > 1:
            self.cart_items[key] -= 1
            self.cart_total -= 1
        elif key in self.cart_items and self.cart_items[key] == 1:
            # Si llega a 1, decrementar elimina el producto
            del self.cart_items[key]
            self.cart_total -= 1
        elif key not in self.cart_items:
            pass
    
    @rx.event
    def remove_from_cart(self, product_id: int):
        """Elimina completamente un producto del carrito"""
        key = str(product_id)
        
        if key in self.cart_items:
            removed_quantity = self.cart_items[key]
            del self.cart_items[key]
            self.cart_total -= removed_quantity

# ===================== CACHE GLOBAL (Fuera de la clase para persistencia) =====================
# Cache compartido entre todas las instancias del State (funciona en producción)
_GLOBAL_PRODUCTS_CACHE: Dict[str, Any] = {
    "all_products": [],
    "popular_products": [], # Popular sigue siendo una query especial
    "timestamp": 0.0
}

class StoreState(rx.State):
    """
    Estado de la tienda que maneja productos y país del usuario.
    Sigue principios POO para encapsular la lógica de estado.
    
    🚀 Implementa State Cache GLOBAL para optimizar rendimiento:
    - Carga TODOS los productos en una sola query.
    - Filtra en memoria para categorías.
    - Cache GLOBAL compartido entre todas las instancias.
    """
    
    # ===================== CONFIGURACIÓN =====================
    CACHE_DURATION: int = 300  # 5 minutos
    
    # ===================== DATOS PÚBLICOS (UI) =====================
    # Cache maestro de productos (copia local del global)
    _all_products_cache: List[Dict[str, Any]] = []
    _popular_products_cache: List[Dict[str, Any]] = []

    # 🚀 OPTIMIZACIÓN: Categorías pre-calculadas (Buckets)
    # Evita iterar _all_products_cache 5 veces en cada render.
    _categorized_products: Dict[str, List[Dict[str, Any]]] = {}
    
    # PRODUCT FEED (INFINITE SCROLL)
    products_feed: List[Dict[str, Any]] = []
    feed_page: int = 0
    feed_limit: int = 12
    feed_has_more: bool = True
    is_loading_feed: bool = False
    
    _products_loaded: bool = False

    # País del usuario para mostrar precios correctos
    user_id: int = 1  # Por defecto usuario de prueba
    
    # Estados de carga
    is_loading: bool = False
    error_message: str = ""

    @rx.var
    def products(self) -> List[Dict[str, Any]]:
        """
        Devuelve TODOS los productos desde el cache maestro.
        """
        return self._all_products_cache

    @rx.event
    def on_load(self):
        """
        Evento que se ejecuta al cargar la página.
        """
        # Cargar productos (usa cache si está disponible)
        self.load_products_cached()
        # Iniciar feed de productos
        if not self.products_feed:
            self.load_more_products()

    @rx.event
    def load_more_products(self):
        """
        Carga la siguiente página de productos para el scroll infinito.
        """
        if self.is_loading_feed or not self.feed_has_more:
            return

        self.is_loading_feed = True
        try:
            # Calcular offset
            offset = self.feed_page * self.feed_limit
            
            # Obtener nuevos productos
            new_products = ProductDataService.get_products_for_store(
                self.user_id, 
                limit=self.feed_limit, 
                offset=offset
            )
            
            if new_products:
                self.products_feed.extend(new_products)
                self.feed_page += 1
                
                # Si recibimos menos del límite, no hay más
                if len(new_products) < self.feed_limit:
                    self.feed_has_more = False
            else:
                self.feed_has_more = False
                
        except Exception as e:
            print(f"❌ Error loading feed: {e}")
        finally:
            self.is_loading_feed = False

    def load_products(self):
        """ Alias para load_products_cached """
        self.load_products_cached()
    
    def _categorize_products(self, products: List[Dict[str, Any]]):
        """
        Categoriza productos en una sola pasada (O(N)).
        """
        import time
        t0 = time.time()
        
        # Reset buckets
        self._categorized_products = {
            "kit de inicio": [],
            "suplemento": [],
            "skincare": [],
            "desinfectante": [],
            "new": []
        }
        
        for p in products:
            p_type = p.get("type")
            if p_type in self._categorized_products:
                self._categorized_products[p_type].append(p)
            
            if p.get("is_new") is True:
                self._categorized_products["new"].append(p)
                
        print(f"⚡ Categorización completada en {time.time() - t0:.4f}s")

    @rx.event
    def load_products_cached(self):
        """
        🚀 Carga centralizada de productos.
        
        Estrategia:
        1. Verificar Cache Global.
        2. Si válido: Copiar a estado local.
        3. Si inválido: 
           - Hacer UNA query para traer TODOS los productos.
           - Hacer una query extra para populares.
           - Actualizar Cache Global.
        """
        import time
        global _GLOBAL_PRODUCTS_CACHE
        
        t_start = time.time()
        print(f"🕒 DEBUG: Inicio load_products_cached - {t_start}")
        
        current_time = time.time()
        last_update = _GLOBAL_PRODUCTS_CACHE.get("timestamp", 0.0)
        cache_age = current_time - last_update
        cache_is_valid = (_GLOBAL_PRODUCTS_CACHE.get("all_products")) and (cache_age < self.CACHE_DURATION)
        
        if cache_is_valid:
            print(f"📦 GLOBAL Cache HIT - Edad: {int(cache_age)}s")
            self._all_products_cache = _GLOBAL_PRODUCTS_CACHE["all_products"]
            self._popular_products_cache = _GLOBAL_PRODUCTS_CACHE["popular_products"]
            # Categorizar también en cache hit porque _categorized_products es instancia local
            self._categorize_products(self._all_products_cache)
            self._products_loaded = True
            print(f"🏁 DEBUG: Fin load_products_cached (HIT) - Total: {time.time() - t_start:.4f}s")
            return

        # Cache MISS - Cargar de DB
        self.is_loading = True
        self.error_message = ""
        print(f"🔍 GLOBAL Cache MISS - Cargando productos de DB...")
        
        t_db_start = time.time()
        
        try:
            # TODO: Integrar con autenticación real
            self.user_id = 1
            
            # 1. Cargar TODOS los productos (Single Query)
            # 🚀 format_product_data_for_store ya fue optimizado en ProductManager
            all_products = ProductDataService.get_products_for_store(self.user_id)
            print(f"📡 DB Query 'All Products' terminada en {time.time() - t_db_start:.4f}s")
            
            # 2. Cargar populares
            t_pop = time.time()
            popular = ProductManager.get_popular_products_formatted(self.user_id, limit=5)
            print(f"📡 DB Query 'Popular' terminada en {time.time() - t_pop:.4f}s")
            
            # Actualizar Global Cache
            _GLOBAL_PRODUCTS_CACHE["all_products"] = all_products
            _GLOBAL_PRODUCTS_CACHE["popular_products"] = popular
            _GLOBAL_PRODUCTS_CACHE["timestamp"] = current_time
            
            # Actualizar Local State
            self._all_products_cache = all_products
            self._popular_products_cache = popular
            
            # Categorizar
            self._categorize_products(all_products)
            
            self._products_loaded = True
            
            print(f"✅ Cache Actualizado: {len(all_products)} productos cargados.")
            
        except Exception as e:
            self.error_message = f"Error cargando productos: {str(e)}"
            print(f"❌ {self.error_message}")
            self._all_products_cache = []
            self._popular_products_cache = []
            self._categorized_products = {}
            
        finally:
            self.is_loading = False
            print(f"🏁 DEBUG: Fin load_products_cached (MISS) - Total: {time.time() - t_start:.4f}s")

    # ===================== GETTERS FILTRADOS (Pre-Calculados) =====================
    # Leen de los buckets O(1) en lugar de filtrar O(N)

    @rx.var
    def latest_products(self) -> List[Dict[str, Any]]:
        """Productos nuevos (is_new=True)"""
        return self._categorized_products.get("new", [])

    @rx.var
    def popular_products(self) -> List[Dict[str, Any]]:
        """Productos populares (cargados aparte)"""
        return self._popular_products_cache

    @rx.var
    def kit_inicio_products(self) -> List[Dict[str, Any]]:
        """Productos tipo 'kit de inicio'"""
        return self._categorized_products.get("kit de inicio", [])

    @rx.var
    def supplement_products(self) -> List[Dict[str, Any]]:
        """Productos tipo 'suplemento'"""
        return self._categorized_products.get("suplemento", [])

    @rx.var
    def skincare_products(self) -> List[Dict[str, Any]]:
        """Productos tipo 'skincare'"""
        return self._categorized_products.get("skincare", [])

    @rx.var
    def sanitize_products(self) -> List[Dict[str, Any]]:
        """Productos tipo 'desinfectante'"""
        return self._categorized_products.get("desinfectante", [])

    @rx.event
    def invalidate_cache(self):
        """Forzar recarga de productos"""
        global _GLOBAL_PRODUCTS_CACHE
        _GLOBAL_PRODUCTS_CACHE["timestamp"] = 0.0
        print("🗑️ Cache invalidado manualmente.")
        self.load_products_cached()

    # Métodos legacy para compatibilidad (redirigen a las properties)
    def get_supplements(self) -> List[Dict[str, Any]]:
        return self.supplement_products
    
    def get_skincare_products(self) -> List[Dict[str, Any]]:
        return self.skincare_products
    
    def get_latest_products_enc(self, limit: int = 6):
        return self.latest_products[:limit]
    
    # Legacy event handlers vacíos o redirigidos si la UI los llama directamente
    @rx.event
    def load_category_products(self):
        self.load_products_cached()

    @rx.event
    def load_category_products_cached(self):
        self.load_products_cached()
