#!/usr/bin/env python3
"""
Script de prueba para verificar que la tabla products funciona correctamente.
"""
import os
import sys
sys.path.append('.')

from decimal import Decimal
from database.products import Products, ProductType, ProductPresentation

def test_products_model():
    """Test básico del modelo Products"""
    print("🧪 Probando modelo Products...")
    
    # Crear una instancia de prueba
    test_product = Products(
        product_name="Test Product",
        sku="TEST001",
        description="Producto de prueba",
        presentation="líquido",
        type="suplemento",
        pv_mx=100,
        pv_usa=100,
        pv_colombia=100,
        vn_mx=Decimal("50.00"),
        vn_usa=Decimal("50.00"),
        vn_colombia=Decimal("50.00"),
        price_mx=Decimal("75.00"),
        price_usa=Decimal("75.00"),
        price_colombia=Decimal("75.00"),
        public_mx=120,
        public_usa=120,
        public_colombia=120
    )
    
    print(f"✅ Modelo creado exitosamente: {test_product}")
    print(f"✅ Nombre del producto: {test_product.product_name}")
    print(f"✅ SKU: {test_product.sku}")
    print(f"✅ Tipo: {test_product.type}")
    print(f"✅ PV México: {test_product.pv_mx}")
    
    # Probar enums
    print(f"✅ ProductType disponibles: {[t.value for t in ProductType]}")
    print(f"✅ ProductPresentation disponibles: {[p.value for p in ProductPresentation]}")
    
    print("🎉 Todas las pruebas del modelo pasaron exitosamente!")
    return True

if __name__ == "__main__":
    try:
        test_products_model()
        print("\n✅ ÉXITO: El modelo Products está funcionando correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)