# Especificaciones Técnicas: OrderState

## Contexto
El UI de órdenes (`orders.py`) está listo y estructurado con componentes reutilizables. Este documento especifica exactamente qué datos y métodos necesita el State para integrarse sin cambios en el diseño.

---

## Archivo actualizado
- `/Users/bradrez/Documents/NNProtect_new_website/NNProtect_new_website/order_service/orders.py`

---

## Estructura de datos requerida

### 1. Datos de una orden (Desktop)

Para la tabla de escritorio, cada orden debe ser un diccionario con estas claves:

```python
{
    'order_id': str,           # ID único para navegación (ej: "uuid-12345")
    'order_number': str,        # Número visible de orden (ej: "12345")
    'shipping_address': str,    # Dirección completa (ej: "Av. Siempre Viva 742, Col. Centro, Colima")
    'purchase_date': str,       # Fecha formateada (ej: "10/09/2025")
    'payment_method': str,      # Método de pago (ej: "Tarjeta crédito", "Billetera digital", "Transferencia", "PayPal")
    'total': str,              # Total con símbolo de moneda (ej: "$1,746.50")
    'status': str              # Estado de la orden (ej: "Entregado", "En proceso", "Cancelado")
}
```

**Función que consume estos datos:** `desktop_order_row(order: dict)`

---

### 2. Datos de una orden (Mobile)

Para las cards móviles, cada orden debe incluir los mismos campos que desktop MÁS:

```python
{
    # Todos los campos de desktop +
    'shipping_status': str,     # Estado de envío (ej: "En camino", "Entregado")
    'payment_status': str,      # Estado de pago (ej: "Pagado", "Pendiente")
    'shipping_alias': str,      # Alias corto de dirección (ej: "Casa", "Oficina")
    'products': list[dict]      # Lista de productos en la orden
}
```

Cada producto dentro de `products` debe tener:

```python
{
    'name': str,      # Nombre del producto (ej: "Dreaming Deep 30 ml")
    'quantity': int   # Cantidad comprada (ej: 2)
}
```

**Funciones que consumen estos datos:**
- `mobile_order_card(order: dict)`
- `mobile_product_item(product: dict)`

---

## Variables del State requeridas

### Estado de datos
```python
# Lista de órdenes (puede ser todas las órdenes del usuario)
orders: list[dict] = []

# Órdenes filtradas según búsqueda y filtros aplicados
filtered_orders: list[dict] = []  # Esta es la que se itera en el UI
```

### Filtros y búsqueda
```python
# Query de búsqueda por número de orden
search_query: str = ""

# Filtro de estado seleccionado
status_filter: str = "Todas"  # Opciones: "Todas", "Pendiente", "En proceso", "Enviado", "Entregado", "Cancelado"

# Criterio de ordenamiento seleccionado
sort_by: str = "Más reciente"  # Opciones: "Más reciente", "Más antiguo", "Mayor monto", "Menor monto"
```

### Paginación (Desktop)
```python
# Página actual (1-indexed para mostrar al usuario)
current_page: int = 1

# Número de órdenes por página
items_per_page: int = 6

# Total de órdenes (después de filtros)
total_orders: int = 0

# Índice de inicio de la página actual para mostrar (ej: "Mostrando 1-6 de 24 órdenes")
current_page_start: int = 1

# Índice final de la página actual
current_page_end: int = 6

# Si estamos en la primera página
is_first_page: bool = True

# Si estamos en la última página
is_last_page: bool = False
```

---

## Métodos del State requeridos

### Setters para filtros y búsqueda
```python
def set_search_query(self, value: str):
    """Actualiza el query de búsqueda y filtra órdenes."""
    self.search_query = value
    self.apply_filters()

def set_status_filter(self, value: str):
    """Actualiza el filtro de estado y filtra órdenes."""
    self.status_filter = value
    self.apply_filters()

def set_sort_by(self, value: str):
    """Actualiza el criterio de ordenamiento y reordena órdenes."""
    self.sort_by = value
    self.apply_filters()
```

### Filtrado y ordenamiento
```python
def apply_filters(self):
    """
    Aplica búsqueda, filtros y ordenamiento a las órdenes.
    Actualiza filtered_orders y reinicia paginación.
    """
    # 1. Filtrar por búsqueda (buscar en order_number)
    # 2. Filtrar por estado (si no es "Todas")
    # 3. Ordenar según sort_by
    # 4. Actualizar total_orders
    # 5. Resetear current_page a 1
    # 6. Actualizar current_page_start y current_page_end
```

### Paginación
```python
def next_page(self):
    """Avanza a la siguiente página."""
    if not self.is_last_page:
        self.current_page += 1
        self.update_pagination_info()

def previous_page(self):
    """Retrocede a la página anterior."""
    if not self.is_first_page:
        self.current_page -= 1
        self.update_pagination_info()

def go_to_page(self, page_number: int):
    """Navega a una página específica."""
    self.current_page = page_number
    self.update_pagination_info()

def update_pagination_info(self):
    """Actualiza current_page_start, current_page_end, is_first_page, is_last_page."""
    # Calcular índices basados en current_page y items_per_page
```

### Descarga de PDF (placeholder para futuro)
```python
def download_pdf(self, order_id: str):
    """Genera y descarga el PDF de una orden."""
    # TODO: Implementar cuando esté disponible el servicio de PDF
    pass
```

---

## Helpers automáticos en el UI

El UI ya incluye estas funciones helper que NO necesitas implementar en el State:

### `get_payment_method_icon(payment_method: str) -> str`
Convierte método de pago en nombre de ícono de Lucide.

**Mapeo:**
- "Tarjeta crédito" / "Tarjeta débito" → "credit-card"
- "Billetera digital" / "PayPal" → "wallet"
- "Transferencia" / "Efectivo" → "banknote"
- Cualquier otro → "credit-card" (default)

### `get_status_color_scheme(status: str) -> str`
Convierte estado en color scheme para badges.

**Mapeo:**
- "Pendiente" → "orange"
- "En proceso" → "blue"
- "Enviado" → "cyan"
- "En camino" → "yellow"
- "Entregado" → "green"
- "Cancelado" → "red"
- Cualquier otro → "gray" (default)

---

## Integración paso a paso

### Paso 1: Importar el State
Descomentar en `/order_service/orders.py` línea 9:
```python
from .order_state import OrderState
```

### Paso 2: Conectar búsqueda (Desktop)
Reemplazar líneas 359-361:
```python
# ANTES (comentado):
# value=OrderState.search_query,
# on_change=OrderState.set_search_query

# DESPUÉS (descomentar):
value=OrderState.search_query,
on_change=OrderState.set_search_query
```

### Paso 3: Conectar filtros (Desktop)
Reemplazar líneas 384-386 y 395-397:
```python
# Filtro de estado
value=OrderState.status_filter,
on_change=OrderState.set_status_filter

# Ordenar por
value=OrderState.sort_by,
on_change=OrderState.set_sort_by
```

### Paso 4: Conectar tabla con datos dinámicos (Desktop)
Reemplazar líneas 420-421:
```python
# ANTES (comentado):
# rx.foreach(OrderState.filtered_orders, desktop_order_row)

# DESPUÉS:
rx.foreach(OrderState.filtered_orders, desktop_order_row)

# Y BORRAR todas las filas hardcodeadas (líneas 423-668)
```

### Paso 5: Conectar paginación (Desktop)
Reemplazar líneas 687-689, 697-699, 724-726:
```python
# Texto de paginación
f"Mostrando {OrderState.current_page_start}-{OrderState.current_page_end} de {OrderState.total_orders} órdenes"

# Botón "Anterior"
disabled=OrderState.is_first_page,
on_click=OrderState.previous_page

# Botón "Siguiente"
disabled=OrderState.is_last_page,
on_click=OrderState.next_page
```

### Paso 6: Conectar búsqueda (Mobile)
Reemplazar líneas 771-773:
```python
value=OrderState.search_query,
on_change=OrderState.set_search_query
```

### Paso 7: Conectar filtros (Mobile)
Reemplazar líneas 799-801 y 810-812:
```python
# Filtro de estado
value=OrderState.status_filter,
on_change=OrderState.set_status_filter

# Ordenar por
value=OrderState.sort_by,
on_change=OrderState.set_sort_by
```

### Paso 8: Conectar cards con datos dinámicos (Mobile)
Reemplazar líneas 821-822:
```python
# ANTES (comentado):
# rx.foreach(OrderState.filtered_orders, mobile_order_card)

# DESPUÉS:
rx.foreach(OrderState.filtered_orders, mobile_order_card)

# Y BORRAR la card hardcodeada (líneas 824-939)
```

---

## Edge cases a considerar en el State

1. **Lista vacía:**
   - Si `filtered_orders` está vacío, mostrar mensaje "No hay órdenes"
   - Puedes agregar un estado: `has_orders: bool`

2. **Búsqueda sin resultados:**
   - `filtered_orders` vacío después de búsqueda
   - Mostrar "No se encontraron órdenes que coincidan con '${search_query}'"

3. **Formato de datos inconsistente:**
   - Siempre retornar strings formateados (no números crudos)
   - Manejar valores nulos o indefinidos con defaults

4. **Paginación:**
   - Si `total_orders < items_per_page`, no mostrar paginación
   - Asegurar que `current_page` nunca exceda el máximo de páginas

5. **Navegación a detalles:**
   - Asegurar que `order_id` sea único y válido
   - El link será: `/orders/order_details?id={order_id}`

---

## Ejemplo de orden completa (para testing)

```python
{
    'order_id': 'abc-123-def-456',
    'order_number': '12345',
    'shipping_address': 'Av. Siempre Viva 742, Col. Centro, Colima',
    'purchase_date': '10/09/2025',
    'payment_method': 'Tarjeta crédito',
    'total': '$1,746.50',
    'status': 'Entregado',
    'shipping_status': 'En camino',
    'payment_status': 'Pagado',
    'shipping_alias': 'Casa',
    'products': [
        {'name': 'Dreaming Deep 30 ml', 'quantity': 2},
        {'name': 'Cúrcuma 30 ml', 'quantity': 1},
        {'name': 'Granada 30 ml', 'quantity': 2}
    ]
}
```

---

## Checklist para Elena

- [ ] Crear archivo `order_state.py` en `/order_service/`
- [ ] Implementar clase `OrderState` con todas las variables listadas
- [ ] Implementar todos los métodos listados
- [ ] Conectar con la base de datos para cargar órdenes del usuario
- [ ] Formatear fechas, montos y estados según los ejemplos
- [ ] Implementar lógica de filtrado en `apply_filters()`
- [ ] Implementar lógica de paginación en los métodos de paginación
- [ ] Crear datos de prueba si es necesario
- [ ] Probar en desktop y mobile
- [ ] Verificar que no haya errores en consola

---

## Contacto

Si necesitas aclaraciones sobre la estructura del UI o los datos requeridos, pregúntame. El diseño está 100% listo, solo falta conectar los datos dinámicos.
