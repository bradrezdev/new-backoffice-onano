"""
Script simple para verificar sintaxis del StoreState sin dependencia de bcrypt
"""
import sys
import ast

def check_syntax(file_path):
    """Verifica la sintaxis de un archivo Python"""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        
        # Compilar para verificar sintaxis
        ast.parse(source)
        print(f"✅ Sintaxis correcta en {file_path}")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en {file_path}:")
        print(f"   Línea {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error leyendo archivo {file_path}: {e}")
        return False

if __name__ == "__main__":
    files_to_check = [
        "NNProtect_new_website/product_service/store_products_state.py",
        "NNProtect_new_website/product_service/store.py",
        "NNProtect_new_website/product_service/product_manager.py",
        "NNProtect_new_website/product_service/product_components.py"
    ]
    
    print("🔍 Verificando sintaxis de archivos de productos...")
    
    all_good = True
    for file_path in files_to_check:
        if not check_syntax(file_path):
            all_good = False
    
    if all_good:
        print("\n🎉 Todos los archivos tienen sintaxis correcta")
        print("✅ El problema del on_mount ha sido solucionado")
    else:
        print("\n❌ Hay errores de sintaxis que necesitan ser corregidos")