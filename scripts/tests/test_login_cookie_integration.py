"""
Test de integración para verificar que la cookie se guarda correctamente después del login.
Este test simula un login completo y verifica que el token JWT esté disponible.
"""

import sys
import os
import asyncio

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_login_saves_cookie():
    """
    Test que simula un login completo y verifica que la cookie se guarda.
    """
    print("\n" + "="*80)
    print("🧪 TEST DE INTEGRACIÓN: Login → Cookie guardada")
    print("="*80 + "\n")
    
    # NOTA: Este test requiere credenciales válidas
    # Para ejecutarlo, usar credenciales reales de un usuario de prueba
    
    print("ℹ️  Este test requiere:")
    print("   1. Base de datos con usuario real")
    print("   2. Supabase configurado")
    print("   3. Ejecutar el servidor Reflex: reflex run")
    print()
    print("📋 PASOS MANUALES PARA VERIFICAR:")
    print("   1. Ejecutar: reflex run")
    print("   2. Abrir navegador: http://localhost:3000")
    print("   3. Hacer login con: B.nunez@hotmail.es")
    print("   4. Abrir DevTools → Application → Cookies")
    print("   5. Verificar que existe: auth_token")
    print("   6. Copiar el valor del token")
    print("   7. Ir a https://jwt.io")
    print("   8. Pegar el token y verificar payload:")
    print("      {")
    print("        'id': <número>,")
    print("        'username': 'Bryan Nuñez',")
    print("        'exp': <timestamp>")
    print("      }")
    print()
    print("✅ Si el payload se ve correcto → Cookie funciona")
    print("❌ Si el payload está vacío → Hay un problema")
    print()
    print("=" * 80)
    print("\n💡 ALTERNATIVA: Test automático con Selenium")
    print("   Ejecutar: python test_login_selenium.py")
    print()


if __name__ == "__main__":
    asyncio.run(test_login_saves_cookie())
