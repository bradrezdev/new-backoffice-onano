import reflex as rx

from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum


class ProductType(Enum):
    """Tipos de productos disponibles"""
    SUPLEMENTO = "suplemento"
    SKINCARE = "skincare"
    DESINFECCION = "desinfección"


class ProductPresentation(Enum):
    """Presentaciones de productos disponibles"""
    KIT = "kit"
    LIQUIDO = "líquido"
    CAPSULAS = "cápsulas"
    SKINCARE = "skincare"


class Products(SQLModel, table=True):
    """
    Modelo de productos del sistema.
    Contiene información de productos con precios y puntos por país.
    
    Campos:
    - Información básica: id, nombre, SKU, descripción
    - Clasificación: presentación, tipo
    - Puntos de valor por país: pv_mx, pv_usa, pv_colombia
    - Valor neto por país: vn_mx, vn_usa, vn_colombia  
    - Precio distribuidor por país: price_mx, price_usa, price_colombia
    - Precio público por país: public_mx, public_usa, public_colombia
    """
    
    id: int | None = Field(default=None, primary_key=True)

    # Información básica del producto
    product_name: str = Field(max_length=255, nullable=False)
    active_ingredient: str = Field(default=None, max_length=255)
    SKU: Optional[str] = Field(default=None, max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    presentation: str = Field(max_length=50, nullable=False, index=True)
    type: str = Field(max_length=50, nullable=False, index=True)
    quantity: str = Field(default=None)

    # Puntos de valor por país
    pv_mx: int = Field(default=0, nullable=False)
    pv_usa: int = Field(default=0, nullable=False)
    pv_colombia: int = Field(default=0, nullable=False)
    
    # Valor neto por país (float)
    vn_mx: float = Field(default=None)
    vn_usa: float = Field(default=None)
    vn_colombia: float = Field(default=None)

    # Precio distribuidor por país (float)
    price_mx: float = Field(default=None)
    price_usa: float = Field(default=None)
    price_colombia: float = Field(default=None)

    # Precio público por país (float, puede ser nulo como en el CSV)
    public_mx: float = Field(default=None)
    public_usa: float = Field(default=None)
    public_colombia: float = Field(default=None)

    # Etiqueta para asignar como "nuevo" a ciertos productos
    is_new: bool = Field(default=False, index=True)

    def get_purchase_count(self, db_session):
        """
        Calcula purchase count dinámicamente desde transactions.
        Evita desincronización de datos redundantes (Principio DRY).
        """
        from database.transactions import Transactions
        return db_session.query(Transactions).filter(
            Transactions.product_id == self.id,
            Transactions.payment_confirmed_at.isnot(None)
        ).count()

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.product_name}', type='{self.type}', is_new={self.is_new})>"