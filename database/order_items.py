import reflex as rx
from sqlmodel import SQLModel, Field


class OrderItems(SQLModel, table=True):
    """
    Items individuales dentro de una orden.
    Cada línea representa un producto y su cantidad.
    Los valores de precio/PV/VN se congelan al agregar al carrito.
    """
    id: int | None = Field(default=None, primary_key=True)
    
    # Relaciones
    order_id: int = Field(foreign_key="orders.id", index=True)
    product_id: int = Field(foreign_key="products.id", index=True)

    # Cantidad
    quantity: int = Field(default=1)

    # Valores congelados al momento de agregar al carrito
    unit_price: float = Field(default=0.0)  # Precio unitario en moneda local
    unit_pv: int = Field(default=0)         # Puntos de volumen unitarios
    unit_vn: float = Field(default=0.0)     # Valor negocio unitario

    # Totales de esta línea (calculados)
    line_total: float = Field(default=0.0)  # quantity * unit_price
    line_pv: int = Field(default=0)         # quantity * unit_pv
    line_vn: float = Field(default=0.0)     # quantity * unit_vn

    def calculate_totals(self):
        """
        Calcula los totales de la línea basado en cantidad y valores unitarios.
        Debe llamarse antes de guardar.
        """
        self.line_total = self.unit_price * self.quantity
        self.line_pv = self.unit_pv * self.quantity
        self.line_vn = self.unit_vn * self.quantity

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"
