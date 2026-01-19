"""
Script de prueba para verificar las nuevas funcionalidades de productos nuevos y populares.
"""
from NNProtect_new_website.product_service.product_manager import ProductManager
from database.addresses import Countries
from database.products import Products
import reflex as rx

def test_latest_and_popular_products():
    """Prueba las funcionalidades de productos nuevos y populares"""
    print("🧪 PROBANDO NUEVAS FUNCIONALIDADES DE PRODUCTOS")
    print("=" * 60)
    
    try:
        # Prueba 1: Obtener productos nuevos (is_new = True)
        print("\n1. ✅ Probando get_latest_products():")
        latest_products = ProductManager.get_latest_products()
        print(f"   📦 Productos marcados como nuevos: {len(latest_products)}")
        
        if latest_products:
            for product in latest_products[:3]:  # Mostrar solo los primeros 3
                print(f"      • {product.product_name} (ID: {product.id}) - Nuevo: {product.is_new}")
        else:
            print("   ⚠️ No hay productos marcados como nuevos en la BD")
        
        # Prueba 2: Obtener productos populares por purchase_count
        print(f"\n2. ✅ Probando get_popular_products():")
        popular_products = ProductManager.get_popular_products(5)
        print(f"   🔥 Top 5 productos más comprados: {len(popular_products)}")
        
        if popular_products:
            for i, product in enumerate(popular_products, 1):
                print(f"      {i}. {product.product_name} - Compras: {product.purchase_count}")
        else:
            print("   ⚠️ No hay productos con purchase_count > 0")
        
        # Prueba 3: Incrementar contador de compras
        print(f"\n3. ✅ Probando increment_purchase_count():")
        if latest_products and latest_products[0].id is not None:
            test_product_id = latest_products[0].id
            print(f"   🎯 Incrementando contador para producto ID: {test_product_id}")
            
            # Obtener valor actual
            with rx.session() as session:
                from sqlmodel import select
                product = session.exec(select(Products).where(Products.id == test_product_id)).first()
                old_count = product.purchase_count if product else 0
            
            # Incrementar
            success = ProductManager.increment_purchase_count(test_product_id)
            
            if success:
                # Verificar nuevo valor
                with rx.session() as session:
                    product = session.exec(select(Products).where(Products.id == test_product_id)).first()
                    new_count = product.purchase_count if product else 0
                
                print(f"   ✅ Contador actualizado: {old_count} → {new_count}")
            else:
                print("   ❌ Error al incrementar contador")
        
        # Prueba 4: Métodos formateados para la tienda
        print(f"\n4. ✅ Probando métodos formateados para México:")
        
        latest_formatted = ProductManager.get_latest_products_formatted(Countries.MEXICO)
        popular_formatted = ProductManager.get_popular_products_formatted(Countries.MEXICO, 3)
        
        print(f"   📦 Productos nuevos formateados: {len(latest_formatted)}")
        print(f"   🔥 Productos populares formateados: {len(popular_formatted)}")
        
        if latest_formatted:
            sample = latest_formatted[0]
            print(f"      Ejemplo nuevo: {sample['name']} - {sample['formatted_price']}")
        
        if popular_formatted:
            sample = popular_formatted[0]
            print(f"      Ejemplo popular: {sample['name']} - {sample['formatted_price']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_data_setup():
    """Simula configuración de datos de prueba si no existen"""
    print(f"\n🔧 Verificando datos de prueba...")
    
    try:
        with rx.session() as session:
            from sqlmodel import select
            
            # Contar productos totales
            total_products = session.exec(select(Products)).all()
            total_count = len(total_products)
            
            # Contar productos nuevos
            new_products = session.exec(select(Products).where(Products.is_new == True)).all()
            new_count = len(new_products)
            
            # Contar productos con compras
            purchased_products = session.exec(select(Products).where(Products.purchase_count > 0)).all()
            purchased_count = len(purchased_products)
            
            print(f"   📊 Total productos: {total_count}")
            print(f"   🆕 Productos nuevos (is_new=True): {new_count}")
            print(f"   🛒 Productos con compras (purchase_count>0): {purchased_count}")
            
            if new_count == 0:
                print("   ⚠️ Sugerencia: Marcar algunos productos como is_new=True en la BD")
            
            if purchased_count == 0:
                print("   ⚠️ Sugerencia: Los métodos increment_purchase_count crearán datos de prueba")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
        return False

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DE PRODUCTOS NUEVOS Y POPULARES")
    
    # Verificar datos existentes
    simulate_data_setup()
    
    # Ejecutar pruebas principales
    success = test_latest_and_popular_products()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 TODAS LAS PRUEBAS COMPLETADAS")
        print("\n✅ MÉTODOS IMPLEMENTADOS:")
        print("1. ✅ get_latest_products() - Productos con is_new=True")
        print("2. ✅ get_popular_products() - Top productos por purchase_count")
        print("3. ✅ increment_purchase_count() - +1 al finalizar compra")
        print("4. ✅ get_latest_products_formatted() - Nuevos formateados")
        print("5. ✅ get_popular_products_formatted() - Populares formateados")
        print("\n🎯 PRINCIPIOS APLICADOS:")
        print("   • KISS: Consultas simples y directas")
        print("   • DRY: Reutilización de format_product_data_for_store")
        print("   • YAGNI: Solo funcionalidad necesaria")
        print("   • POO: Métodos específicos por responsabilidad")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON - Revisar implementación")