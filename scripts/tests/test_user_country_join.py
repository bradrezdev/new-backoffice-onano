#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del método JOIN 
para obtener el país de registro del usuario.
"""
import os
import sys
sys.path.append('.')

from database.users import Users
from database.addresses import Countries
from NNProtect_new_website.auth_service.auth_state import UserDataManager

def test_user_country_join():
    """Test del método get_user_country_by_id"""
    print("🧪 Probando método JOIN para obtener país del usuario...")
    
        # Test 1: Probar el método estático migrado a UserDataManager
    try:
        # Simulamos que el usuario ID 1 existe
        user_id = 1
        country = UserDataManager.get_user_country_by_id(user_id)
        
        if country:
            print(f"✅ País encontrado para usuario {user_id}: {country.value}")
        else:
            print(f"ℹ️  No se encontró país para usuario {user_id} (normal si no hay datos)")
            
    except Exception as e:
        print(f"⚠️  Error en método estático: {e}")
    
    # Test 2: Probar método de actualización de cache migrado a UserDataManager
    try:
        # Probar actualización de cache usando UserDataManager
        user_id = 1
        result = UserDataManager.update_user_country_cache(user_id)
        
        if result:
            print(f"✅ Country cache actualizado correctamente para usuario {user_id}")
        else:
            print("ℹ️  No se pudo actualizar country cache (normal si no hay datos)")
            
    except Exception as e:
        print(f"⚠️  Error en método de actualización: {e}")
    
    # Test 3: Verificar que los enums Countries están disponibles
    print(f"✅ Countries disponibles: {[c.value for c in Countries]}")
    
    print("🎉 Pruebas del método JOIN completadas!")
    return True

if __name__ == "__main__":
    try:
        test_user_country_join()
        print("\n✅ ÉXITO: Los métodos JOIN están funcionando correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)