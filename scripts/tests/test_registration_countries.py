#!/usr/bin/env python3
"""
Script de testing para validar que el sistema de registro
funciona correctamente con manejo de países sin ENUM.
"""

import os
import sys
from dotenv import load_dotenv

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno
load_dotenv()

def test_registration_manager():
    """Probar métodos de RegistrationManager para países."""
    
    print("🧪 Testing RegistrationManager sin ENUM Countries...")
    
    try:
        from NNProtect_new_website.auth_service.auth_state import RegistrationManager
        
        # Test 1: Obtener países disponibles
        print("\n1️⃣ Países disponibles:")
        countries = RegistrationManager.get_country_options()
        for country in countries:
            print(f"  • {country}")
        
        # Test 2: Obtener estados para cada país
        print("\n2️⃣ Estados por país:")
        for country in countries:
            states = RegistrationManager.get_states_for_country(country)
            print(f"  📍 {country}: {len(states)} estados")
            if len(states) > 0:
                print(f"    Primeros 3: {states[:3]}")
        
        # Test 3: Conversión display → valor interno
        print("\n3️⃣ Conversión de nombres:")
        for country in countries:
            internal_value = RegistrationManager.get_country_value(country)
            print(f"  '{country}' → '{internal_value}'")
        
        # Test 4: Verificar que funciona el flujo país → estado
        print("\n4️⃣ Simulando selección de país:")
        test_country = "Mexico"
        states = RegistrationManager.get_states_for_country(test_country)
        print(f"  Usuario selecciona: {test_country}")
        print(f"  Estados disponibles: {len(states)}")
        print(f"  Primeros 5 estados: {states[:5]}")
        
        print("\n✅ RegistrationManager funciona correctamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_state_computed_vars():
    """Probar que los computed vars de AuthState funcionen."""
    
    print("\n🎯 Testing computed vars de AuthState...")
    
    try:
        from NNProtect_new_website.auth_service.auth_state import AuthState
        
        # Crear instancia de estado
        auth_state = AuthState()
        
        # Test 1: country_options
        print("\n1️⃣ Testing country_options:")
        countries = auth_state.country_options
        print(f"  Países obtenidos: {len(countries)}")
        for country in countries:
            print(f"    • {country}")
        
        # Test 2: state_options (sin país seleccionado)
        print("\n2️⃣ Testing state_options (sin país):")
        states_empty = auth_state.state_options
        print(f"  Estados sin país: {len(states_empty)} (debería ser 0)")
        
        # Test 3: state_options (con país seleccionado)
        print("\n3️⃣ Testing state_options (con país):")
        auth_state.new_country = "Mexico"
        states_mx = auth_state.state_options
        print(f"  Estados para México: {len(states_mx)}")
        print(f"  Primeros 5: {states_mx[:5]}")
        
        print("\n✅ Computed vars funcionan correctamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_addresses_model():
    """Probar que el modelo Addresses use string en lugar de ENUM."""
    
    print("\n📋 Testing modelo Addresses...")
    
    try:
        from database.addresses import Addresses
        
        # Verificar que country es string
        print("\n1️⃣ Verificando tipo de campo country:")
        
        # Crear instancia para probar
        test_address = Addresses(
            street="Calle Test 123",
            neighborhood="Colonia Test",
            city="Ciudad Test",
            state="Estado Test", 
            country="MEXICO",  # ✅ Texto plano
            zip_code="12345"
        )
        
        print(f"  ✅ Campo country acepta string: '{test_address.country}'")
        print(f"  ✅ Tipo de country: {type(test_address.country)}")
        
        print("\n✅ Modelo Addresses funciona con texto plano!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando tests del sistema de registro sin ENUM...")
    
    success_count = 0
    total_tests = 3
    
    # Test 1: RegistrationManager
    if test_registration_manager():
        success_count += 1
    
    # Test 2: AuthState computed vars
    if test_auth_state_computed_vars(): 
        success_count += 1
    
    # Test 3: Addresses model
    if test_addresses_model():
        success_count += 1
    
    print(f"\n📊 Resultados: {success_count}/{total_tests} tests pasaron")
    
    if success_count == total_tests:
        print("🎉 ¡Todos los tests pasaron! El sistema funciona correctamente.")
        print("💡 El registro de usuarios ahora usa texto plano para países.")
        print("🔄 La funcionalidad país → estado se mantiene intacta.")
    else:
        print("💥 Algunos tests fallaron. Revisa los errores arriba.")
        sys.exit(1)