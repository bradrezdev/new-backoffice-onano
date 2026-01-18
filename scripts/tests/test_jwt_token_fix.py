"""
Test específico para verificar que JWT encode/decode funciona correctamente.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from NNProtect_new_website.auth_service.auth_state import AuthenticationManager
from database.users import Users
from unittest.mock import Mock


def test_jwt_encode_decode_cycle():
    """
    Test el ciclo completo de encode y decode del JWT token.
    """
    print("\n" + "="*80)
    print("🧪 TEST: Ciclo completo JWT encode → decode")
    print("="*80 + "\n")
    
    # Arrange: Crear un usuario mock
    mock_user = Mock(spec=Users)
    mock_user.id = 1
    mock_user.first_name = "Bryan"
    mock_user.last_name = "Nuñez"
    
    print(f"👤 Usuario mock creado: {mock_user.first_name} {mock_user.last_name} (ID: {mock_user.id})")
    
    # Act 1: Generar token
    print(f"\n🔐 PASO 1: Generando token JWT...")
    try:
        token = AuthenticationManager.create_jwt_token(mock_user)
        print(f"✅ Token generado exitosamente")
        print(f"📏 Longitud del token: {len(token)} caracteres")
        print(f"🔤 Primeros 100 chars: {token[:100]}...")
        
        # Verificar estructura del JWT (debe tener 3 partes separadas por puntos)
        parts = token.split('.')
        print(f"🧩 Partes del JWT: {len(parts)} (debe ser 3)")
        assert len(parts) == 3, f"JWT debe tener 3 partes, pero tiene {len(parts)}"
        print(f"   ✅ Header: {parts[0][:20]}...")
        print(f"   ✅ Payload: {parts[1][:20]}...")
        print(f"   ✅ Signature: {parts[2][:20]}...")
        
    except Exception as e:
        print(f"❌ ERROR generando token: {e}")
        raise
    
    # Act 2: Decodificar token
    print(f"\n🔓 PASO 2: Decodificando token JWT...")
    try:
        decoded_payload = AuthenticationManager.decode_jwt_token(token)
        print(f"✅ Token decodificado exitosamente")
        print(f"📦 Payload completo: {decoded_payload}")
        
    except Exception as e:
        print(f"❌ ERROR decodificando token: {e}")
        raise
    
    # Assert: Verificar que el payload contiene los datos correctos
    print(f"\n✓ PASO 3: Verificando contenido del payload...")
    
    assert decoded_payload != {}, "❌ Payload no debe estar vacío"
    print(f"   ✅ Payload no está vacío")
    
    assert "id" in decoded_payload, "❌ Payload debe contener 'id'"
    print(f"   ✅ Contiene 'id': {decoded_payload.get('id')}")
    
    assert decoded_payload["id"] == 1, f"❌ ID debe ser 1, pero es {decoded_payload['id']}"
    print(f"   ✅ ID correcto: {decoded_payload['id']}")
    
    assert "username" in decoded_payload, "❌ Payload debe contener 'username'"
    print(f"   ✅ Contiene 'username': {decoded_payload.get('username')}")
    
    assert decoded_payload["username"] == "Bryan Nuñez", f"❌ Username incorrecto: {decoded_payload['username']}"
    print(f"   ✅ Username correcto: {decoded_payload['username']}")
    
    assert "exp" in decoded_payload, "❌ Payload debe contener 'exp' (expiration)"
    print(f"   ✅ Contiene 'exp': {decoded_payload.get('exp')}")
    
    print("\n" + "="*80)
    print("✅ TEST PASSED: JWT encode/decode funciona correctamente")
    print("="*80 + "\n")
    
    return True


def test_jwt_with_invalid_token():
    """
    Test que un token inválido retorna payload vacío.
    """
    print("\n" + "="*80)
    print("🧪 TEST: Token inválido debe retornar payload vacío")
    print("="*80 + "\n")
    
    # Test 1: Token completamente inválido
    print("🔍 Test 1: Token sin estructura JWT...")
    invalid_token = "esto-no-es-un-jwt-valido"
    decoded = AuthenticationManager.decode_jwt_token(invalid_token)
    assert decoded == {}, f"❌ Debe retornar dict vacío, pero retornó: {decoded}"
    print("   ✅ Retorna dict vacío correctamente")
    
    # Test 2: Token con estructura pero signature incorrecta
    print("\n🔍 Test 2: Token con signature incorrecta...")
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJUZXN0In0.firma_incorrecta"
    decoded = AuthenticationManager.decode_jwt_token(fake_token)
    assert decoded == {}, f"❌ Debe retornar dict vacío, pero retornó: {decoded}"
    print("   ✅ Retorna dict vacío correctamente")
    
    # Test 3: Token vacío
    print("\n🔍 Test 3: Token vacío...")
    empty_token = ""
    decoded = AuthenticationManager.decode_jwt_token(empty_token)
    assert decoded == {}, f"❌ Debe retornar dict vacío, pero retornó: {decoded}"
    print("   ✅ Retorna dict vacío correctamente")
    
    print("\n" + "="*80)
    print("✅ TEST PASSED: Tokens inválidos manejados correctamente")
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  🧪 TESTS DE JWT TOKEN - DIAGNÓSTICO".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝\n")
    
    try:
        # Test 1: Ciclo completo
        test_jwt_encode_decode_cycle()
        
        # Test 2: Tokens inválidos
        test_jwt_with_invalid_token()
        
        print("\n" + "╔" + "═"*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "  ✅ TODOS LOS TESTS PASARON".center(78) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "═"*78 + "╝\n")
        
        print("🎯 CONCLUSIÓN:")
        print("   • JWT encode funciona correctamente")
        print("   • JWT decode funciona correctamente")
        print("   • Payload contiene los datos esperados (id, username, exp)")
        print("   • Tokens inválidos se manejan correctamente")
        print("\n✨ El problema NO está en create_jwt_token() ni decode_jwt_token()")
        print("✨ El problema debe estar en CÓMO o CUÁNDO se guarda el token en la cookie")
        
    except AssertionError as e:
        print("\n" + "╔" + "═"*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "  ❌ TEST FAILED".center(78) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "═"*78 + "╝\n")
        print(f"🔥 Error: {e}")
        sys.exit(1)
    
    except Exception as e:
        print("\n" + "╔" + "═"*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "  ❌ EXCEPTION".center(78) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "═"*78 + "╝\n")
        print(f"🔥 Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
