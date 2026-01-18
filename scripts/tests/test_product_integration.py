"""
Script de prueba para verificar que la integración de productos funcione.
"""
import reflex as rx
from NNProtect_new_website.product_service.product_data.product_data_service import ProductDataService
from database.addresses import Countries

def test_product_integration():
    """Prueba la integración completa de productos"""
    print("🧪 Probando integración de productos en la tienda...")
    
    try:
        # Probar para diferentes países
        countries_to_test = [Countries.MEXICO, Countries.USA, Countries.COLOMBIA]
        
        for country in countries_to_test:
            print(f"\n🌍 Probando productos para {country.value}:")
            
            # Obtener productos para el país
            products = ProductDataService.get_products_for_store(country)
            
            if not products:
                print(f"❌ No se encontraron productos para {country.value}")
                continue
                
            print(f"✅ Encontrados {len(products)} productos")
            
            # Mostrar los primeros 3 productos como muestra
            for i, product in enumerate(products[:3]):
                print(f"  📦 Producto {i+1}:")
                print(f"     Nombre: {product['name']}")
                print(f"     Precio: {product['formatted_price']}")
                print(f"     PV: {product['pv']}")
                print(f"     Tipo: {product['type']}")
            
            # Probar filtros por tipo
            supplements = ProductDataService.get_products_by_type(country, "suplemento")
            skincare = ProductDataService.get_products_by_type(country, "skincare")
            
            print(f"  💊 Suplementos: {len(supplements)}")
            print(f"  🧴 Skincare: {len(skincare)}")
        
        print("\n🎉 Prueba de integración completada exitosamente")
        return True
            
    except Exception as e:
        print(f"❌ Error en prueba de integración: {e}")
        return False

if __name__ == "__main__":
    test_product_integration()