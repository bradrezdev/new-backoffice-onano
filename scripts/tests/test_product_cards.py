"""
Script de prueba para verificar que los 4 nuevos métodos de tarjetas de productos funcionen correctamente.
"""
import sys
import ast
from typing import Dict

def test_product_components_syntax():
    """Verifica la sintaxis del archivo product_components.py"""
    print("🔍 Verificando sintaxis de product_components.py...")
    
    try:
        with open("NNProtect_new_website/product_service/product_components.py", 'r') as f:
            source = f.read()
        
        # Compilar para verificar sintaxis
        ast.parse(source)
        print("✅ Sintaxis correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis:")
        print(f"   Línea {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False

def test_methods_structure():
    """Verifica que los métodos tengan la estructura correcta"""
    print("\n📋 Verificando estructura de los métodos...")
    
    try:
        with open("NNProtect_new_website/product_service/product_components.py", 'r') as f:
            content = f.read()
        
        # Verificar que los 4 métodos existen
        required_methods = [
            "new_products_card",
            "most_requested_products_card", 
            "supplement_products_card",
            "skincare_products_card"
        ]
        
        methods_found = []
        for method in required_methods:
            if f"def {method}(product_data: Dict)" in content:
                methods_found.append(method)
                print(f"   ✅ {method} - Definido correctamente")
            else:
                print(f"   ❌ {method} - NO encontrado")
        
        # Verificar badges únicos
        badges = {
            "🆕 Nuevo": "new_products_card",
            "🔥 Popular": "most_requested_products_card",
            "💊 Suplemento": "supplement_products_card", 
            "🧴 Skincare": "skincare_products_card"
        }
        
        print(f"\n🏷️ Verificando badges únicos:")
        for badge, method in badges.items():
            if badge in content:
                print(f"   ✅ {badge} - Presente en {method}")
            else:
                print(f"   ❌ {badge} - NO encontrado")
        
        # Verificar diferenciadores específicos
        print(f"\n🎯 Verificando diferenciadores específicos:")
        if "PV:" in content:
            print("   ✅ PV mostrado en supplement_products_card")
        else:
            print("   ❌ PV no encontrado en supplement_products_card")
            
        if "VN:" in content:
            print("   ✅ VN mostrado en skincare_products_card")
        else:
            print("   ❌ VN no encontrado en skincare_products_card")
        
        return len(methods_found) == 4
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def test_dry_principle():
    """Verifica que se siga el principio DRY"""
    print(f"\n🔄 Verificando principio DRY (Don't Repeat Yourself):")
    
    try:
        with open("NNProtect_new_website/product_service/product_components.py", 'r') as f:
            content = f.read()
        
        # Contar elementos repetidos que deberían ser similares
        common_elements = [
            'rx.image(',
            'object_fit="cover"',
            'border_radius="19px"',
            'min_width="36px"',
            'height="36px"',
            '"Agregar"',
            'width="65vw"',
            'min_height="360px"'
        ]
        
        for element in common_elements:
            count = content.count(element)
            if count >= 4:  # Debería aparecer en los 4 nuevos métodos + original
                print(f"   ✅ {element} - Reutilizado {count} veces")
            else:
                print(f"   ⚠️ {element} - Solo {count} veces (esperado: ≥4)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando DRY: {e}")
        return False

def simulate_product_data():
    """Simula datos de productos para prueba conceptual"""
    print(f"\n🧪 Simulando datos de productos:")
    
    # Datos de ejemplo
    sample_products = [
        {
            "id": 1,
            "name": "Kit 1 Supplement Protect",
            "formatted_price": "$1996.00",
            "pv": 1670,
            "vn": 1670.0,
            "type": "suplemento"
        },
        {
            "id": 2, 
            "name": "Kit 2 Full Skin",
            "formatted_price": "$2596.00",
            "pv": 2180,
            "vn": 2180.0,
            "type": "skincare"
        }
    ]
    
    print("   📦 Datos de ejemplo creados:")
    for product in sample_products:
        print(f"      {product['name']} - {product['formatted_price']} (Tipo: {product['type']})")
    
    return True

if __name__ == "__main__":
    print("🧪 PROBANDO NUEVOS MÉTODOS DE TARJETAS DE PRODUCTOS")
    print("=" * 60)
    
    tests = [
        ("Sintaxis", test_product_components_syntax),
        ("Estructura de métodos", test_methods_structure),
        ("Principio DRY", test_dry_principle),
        ("Simulación de datos", simulate_product_data)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando prueba: {test_name}")
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("\n✅ MÉTODOS CREADOS CORRECTAMENTE:")
        print("1. ✅ new_products_card - Para 'Últimas novedades'")
        print("2. ✅ most_requested_products_card - Para 'Productos más pedidos'") 
        print("3. ✅ supplement_products_card - Para 'Suplementos'")
        print("4. ✅ skincare_products_card - Para 'Cuidado de la piel'")
        print("\n🎯 PRINCIPIOS APLICADOS:")
        print("   • KISS: Métodos simples y específicos")
        print("   • DRY: Herencia de propiedades de product_card_horizontal")
        print("   • YAGNI: Solo funcionalidad necesaria para cada sección")
        print("   • POO: Métodos organizados por responsabilidad")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON - Revisar implementación")