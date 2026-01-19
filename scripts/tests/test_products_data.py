"""
Script para verificar los datos existentes en la tabla products
"""
import reflex as rx
from database.products import Products

def test_products_data():
    """Consulta todos los productos en la tabla para ver estructura de datos"""
    print("🔍 Consultando datos existentes en tabla products...")
    
    try:
        with rx.session() as session:
            # Obtener todos los productos
            products = session.query(Products).all()
            
            if not products:
                print("❌ No hay productos en la tabla")
                return
            
            print(f"✅ Encontrados {len(products)} productos en la tabla")
            print("\n📋 Estructura de datos:")
            
            # Mostrar los primeros 3 productos como muestra
            for i, product in enumerate(products[:3]):
                print(f"\n--- Producto {i+1} ---")
                print(f"ID: {product.id}")
                print(f"Nombre: {product.product_name}")
                print(f"SKU: {product.SKU}")
                print(f"Tipo: {product.type}")
                print(f"Presentación: {product.presentation}")
                print(f"Descripción: {product.description}")
                print(f"PV México: {product.pv_mx}")
                print(f"PV USA: {product.pv_usa}")
                print(f"PV Colombia: {product.pv_colombia}")
                print(f"Precio México: {product.price_mx}")
                print(f"Precio USA: {product.price_usa}")
                print(f"Precio Colombia: {product.price_colombia}")
                print(f"VN México: {product.vn_mx}")
                print(f"VN USA: {product.vn_usa}")
                print(f"VN Colombia: {product.vn_colombia}")
            
            if len(products) > 3:
                print(f"\n... y {len(products) - 3} productos más")
                
    except Exception as e:
        print(f"❌ Error consultando productos: {e}")

if __name__ == "__main__":
    test_products_data()