"""
Estado para la gestión de órdenes del usuario.
Maneja carga, filtrado, búsqueda y paginación de órdenes.
"""
import reflex as rx
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from ..backend.order_service import OrderService
from ...auth.state.auth_state import AuthState


class OrderState(rx.State):
    """
    Estado reactivo para gestión de órdenes del usuario.
    Sigue principios POO y arquitectura service-oriented del proyecto.
    """

    # Lista de órdenes del usuario
    _orders: List[Dict[str, Any]] = []
    _orders_loaded: bool = False

    # Filtros activos
    selected_status: str = "Todas"
    search_query: str = ""
    sort_by: str = "Más reciente"

    # Paginación
    current_page: int = 1
    items_per_page: int = 6
    total_orders: int = 0

    # Estados de carga
    is_loading: bool = False
    error_message: str = ""

    # User ID del usuario logueado
    user_member_id: Optional[int] = None

    @rx.var
    def orders(self) -> List[Dict[str, Any]]:
        """
        Propiedad computada que retorna órdenes filtradas y paginadas.
        Aplica filtros, búsqueda, ordenamiento y paginación.
        """
        if not self._orders:
            return []

        # Aplicar filtrado por estado
        filtered_orders = self._filter_by_status(self._orders, self.selected_status)

        # Aplicar búsqueda por número de orden
        if self.search_query.strip():
            filtered_orders = self._filter_by_search(filtered_orders, self.search_query)

        # Aplicar ordenamiento
        sorted_orders = self._apply_sorting(filtered_orders, self.sort_by)

        # Actualizar total de órdenes después de filtros
        self.total_orders = len(sorted_orders)

        # Aplicar paginación
        paginated_orders = self._apply_pagination(sorted_orders, self.current_page, self.items_per_page)

        return paginated_orders

    @rx.var
    def total_pages(self) -> int:
        """Calcula el número total de páginas"""
        if self.total_orders == 0:
            return 1
        return (self.total_orders + self.items_per_page - 1) // self.items_per_page

    @rx.var
    def showing_from(self) -> int:
        """Índice del primer item mostrado"""
        if self.total_orders == 0:
            return 0
        return (self.current_page - 1) * self.items_per_page + 1

    @rx.var
    def showing_to(self) -> int:
        """Índice del último item mostrado"""
        if self.total_orders == 0:
            return 0
        max_item = self.current_page * self.items_per_page
        return min(max_item, self.total_orders)

    @rx.event
    async def on_load(self):
        """
        Evento que se ejecuta al cargar la página.
        Carga las órdenes del usuario automáticamente.
        """
        # Obtener estado de autenticación
        auth_state = await self.get_state(AuthState)

        if auth_state.is_logged_in and auth_state.logged_user_data:
            self.user_member_id = auth_state.logged_user_data.get("member_id")
            
            if self.user_member_id:
                print(f"✅ OrderState inicializado para member_id={self.user_member_id}")
                self.load_orders()
            else:
                self.error_message = "No se encontró ID de miembro en sesión"
                print("⚠️ logged_user_data no tiene member_id")
        else:
            # Fallback para pruebas si no hay usuario real (temporal)
            # self.user_member_id = 1
            # self.load_orders()
            # print("⚠️ Usando ID 1 temporal para pruebas en OrderState")
            
            print("⚠️ Usuario no logueado en OrderState")
            self.error_message = "Debes iniciar sesión para ver tus órdenes"
            # Opcional: Redirigir a login
            # return rx.redirect("/login")

    @rx.event
    def load_orders(self):
        """
        Carga todas las órdenes del usuario desde la base de datos.
        """
        if self.user_member_id is None:
            self.error_message = "Usuario no identificado"
            return

        self.is_loading = True
        self.error_message = ""

        try:
            # Cargar órdenes usando el servicio
            self._orders = OrderService.get_user_orders(self.user_member_id)
            self._orders_loaded = True
            self.total_orders = len(self._orders)

            print(f"✅ Cargadas {len(self._orders)} órdenes para member_id={self.user_member_id}")

        except Exception as e:
            self.error_message = f"Error cargando órdenes: {str(e)}"
            print(f"❌ {self.error_message}")
            import traceback
            traceback.print_exc()

        finally:
            self.is_loading = False

    @rx.event
    def filter_by_status(self, status: str):
        """
        Cambia el filtro de estado y resetea a la primera página.
        """
        self.selected_status = status
        self.current_page = 1  # Resetear a primera página al cambiar filtro

    @rx.event
    def search_orders(self, query: str):
        """
        Busca órdenes por número de orden.
        """
        self.search_query = query
        self.current_page = 1  # Resetear a primera página al buscar

    @rx.event
    def sort_orders(self, sort_option: str):
        """
        Cambia el ordenamiento de las órdenes.
        """
        self.sort_by = sort_option
        self.current_page = 1  # Resetear a primera página al cambiar ordenamiento

    @rx.event
    def go_to_page(self, page_number: int):
        """
        Navega a una página específica.
        """
        if 1 <= page_number <= self.total_pages:
            self.current_page = page_number

    @rx.event
    def next_page(self):
        """Avanza a la siguiente página"""
        if self.current_page < self.total_pages:
            self.current_page += 1

    @rx.event
    def previous_page(self):
        """Retrocede a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1

    # Métodos helper privados (no reactivos)

    def _filter_by_status(self, orders: List[Dict[str, Any]], status: str):
        """
        Filtra órdenes por estado.
        Mapea estados del UI a estados de la BD.
        """
        if status == "Todas":
            return orders

        # Mapeo de estados UI -> BD
        status_map = {
            "Pendiente de pago": ["draft", "pending_payment"],
            "Pagado / En proceso": ["payment_confirmed", "processing"],
            "Enviado": ["shipped"],
            "Entregado": ["delivered"],
            "Cancelado": ["cancelled", "refunded"]
        }

        db_statuses = status_map.get(status, [])
        if not db_statuses:
            return orders

        return [order for order in orders if order["status_raw"] in db_statuses]

    def _filter_by_search(self, orders: List[Dict[str, Any]], query: str):
        """
        Filtra órdenes por número de orden (búsqueda parcial).
        """
        query_lower = query.lower().strip()
        return [
            order for order in orders
            if query_lower in str(order["order_number"]).lower()
        ]

    def _apply_sorting(self, orders: List[Dict[str, Any]], sort_option: str):
        """
        Ordena órdenes según el criterio seleccionado.
        """
        if sort_option == "Más reciente":
            return sorted(orders, key=lambda x: x["created_at_raw"], reverse=True)
        elif sort_option == "Más antiguo":
            return sorted(orders, key=lambda x: x["created_at_raw"])
        elif sort_option == "Mayor monto":
            return sorted(orders, key=lambda x: x["total"], reverse=True)
        elif sort_option == "Menor monto":
            return sorted(orders, key=lambda x: x["total"])
        else:
            return orders

    def _apply_pagination(self, orders: List[Dict[str, Any]], page: int, per_page: int):
        """
        Aplica paginación a la lista de órdenes.
        """
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        return orders[start_idx:end_idx]


class OrderDetailState(rx.State):
    """
    Estado para vista de detalle de una orden específica.
    """

    # Orden seleccionada
    order_id: Optional[int] = None
    order_data: Optional[Dict[str, Any]] = None
    order_items: List[Dict[str, Any]] = []

    # Estados de carga
    is_loading: bool = False
    error_message: str = ""

    @rx.event
    async def load_order_from_url(self):
        """
        Carga la orden desde el parámetro 'id' en la URL.
        Se llama en on_mount de la página order_details.
        """
        try:
            # Obtener el parámetro 'id' de la URL
            order_id_str = self.router.page.params.get("id", "")
            
            if not order_id_str:
                self.error_message = "No se especificó ID de orden en la URL"
                print("⚠️ No hay parámetro 'id' en la URL")
                return
            
            # Convertir a int y cargar
            order_id = int(order_id_str)
            await self.load_order_details(order_id)
            
        except ValueError as e:
            self.error_message = "ID de orden inválido"
            print(f"⚠️ ID de orden inválido: {order_id_str if 'order_id_str' in locals() else 'N/A'}")
        except Exception as e:
            self.error_message = f"Error cargando orden: {str(e)}"
            print(f"❌ Error en load_order_from_url: {e}")
            import traceback
            traceback.print_exc()

    @rx.event
    async def load_order_details(self, order_id: int):
        """
        Carga los detalles completos de una orden específica.
        Incluye información de la orden y sus items.
        """
        self.is_loading = True
        self.error_message = ""
        self.order_id = order_id

        try:
            # Cargar orden completa con items
            result = OrderService.get_order_details(order_id)

            if result:
                self.order_data = result["order"]
                self.order_items = result["items"]
                print(f"✅ Detalles cargados para orden #{order_id}")
            else:
                self.error_message = f"Orden #{order_id} no encontrada"

        except Exception as e:
            self.error_message = f"Error cargando detalles: {str(e)}"
            print(f"❌ {self.error_message}")
            import traceback
            traceback.print_exc()

        finally:
            self.is_loading = False

    @rx.event
    def clear_order_details(self):
        """Limpia el estado al salir de la vista de detalles"""
        self.order_id = None
        self.order_data = None
        self.order_items = []
        self.error_message = ""
