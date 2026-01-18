"""
═══════════════════════════════════════════════════════════════════════════════
🔧 SCRIPT DE CORRECCIÓN: Recalcular PVG_CACHE para todos los usuarios (SQL DIRECTO)
═══════════════════════════════════════════════════════════════════════════════

PROBLEMA:
El bug en admin_state.py causó que pvg_cache no incluyera el pv_cache del usuario.

SOLUCIÓN:
Recalcular pvg_cache para TODOS los usuarios con la fórmula correcta:
PVG = PV_personal + Σ(PV_descendientes)

AUTOR: Arquitecto de Datos
FECHA: 31 de octubre de 2025
"""

import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Obtiene conexión a la base de datos desde DATABASE_URL."""
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("❌ Error: DATABASE_URL no está configurada")
        return None
    
    # Parse URL
    result = urlparse(db_url)
    
    try:
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port,
            database=result.path[1:],
            user=result.username,
            password=result.password
        )
        return conn
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def recalculate_pvg_for_all_users():
    """
    Recalcula el pvg_cache para todos los usuarios usando SQL directo.
    
    Algoritmo:
    1. Para cada usuario, obtener su pv_cache
    2. Obtener todos sus descendientes
    3. Sumar el pv_cache de todos los descendientes
    4. PVG = PV_personal + Σ(PV_descendientes)
    """
    
    print("\n═══════════════════════════════════════════════════════════════════════════════")
    print("🔧 RECALCULANDO PVG_CACHE PARA TODOS LOS USUARIOS (SQL DIRECTO)")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Obtener TODOS los usuarios
        cursor.execute("SELECT member_id, first_name, last_name, pv_cache, pvg_cache FROM users ORDER BY member_id")
        users = cursor.fetchall()
        
        print(f"📊 Total de usuarios a procesar: {len(users)}\n")
        
        corrections_made = 0
        users_correct = 0
        
        for user_row in users:
            member_id, first_name, last_name, pv_cache, current_pvg = user_row
            full_name = f"{first_name} {last_name}"
            
            # 1. El PVG mínimo es el PV del usuario
            expected_pvg = pv_cache
            
            # 2. Obtener todos los descendientes y sumar su PV
            cursor.execute("""
                SELECT SUM(u.pv_cache)
                FROM usertreepaths utp
                JOIN users u ON u.member_id = utp.descendant_id
                WHERE utp.ancestor_id = %s
                  AND utp.depth > 0
            """, (member_id,))
            
            result = cursor.fetchone()
            descendants_pv = result[0] if result[0] is not None else 0
            expected_pvg += descendants_pv
            
            # 3. Comparar con el pvg_cache actual
            if current_pvg != expected_pvg:
                print(f"   ❌ Member {member_id} ({full_name}):")
                print(f"      PV personal: {pv_cache}")
                print(f"      PV descendientes: {descendants_pv}")
                print(f"      PVG actual: {current_pvg}")
                print(f"      PVG esperado: {expected_pvg}")
                print(f"      Diferencia: {expected_pvg - current_pvg}\n")
                
                # Corregir
                cursor.execute("""
                    UPDATE users
                    SET pvg_cache = %s
                    WHERE member_id = %s
                """, (expected_pvg, member_id))
                
                corrections_made += 1
            else:
                users_correct += 1
        
        # Guardar cambios
        conn.commit()
        
        print(f"\n═══════════════════════════════════════════════════════════════════════════════")
        print(f"✅ CORRECCIÓN COMPLETADA")
        print(f"═══════════════════════════════════════════════════════════════════════════════\n")
        print(f"   📊 Total usuarios: {len(users)}")
        print(f"   ✅ Usuarios correctos: {users_correct}")
        print(f"   🔧 Correcciones realizadas: {corrections_made}")
        print(f"\n═══════════════════════════════════════════════════════════════════════════════\n")
        
        cursor.close()
        
    except Exception as e:
        print(f"\n❌ Error durante la corrección: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

def verify_pvg_calculation():
    """
    Verifica que todos los usuarios tengan pvg_cache >= pv_cache.
    Esta es una validación rápida post-corrección.
    """
    
    print("\n═══════════════════════════════════════════════════════════════════════════════")
    print("🔍 VERIFICANDO CÁLCULO DE PVG")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Buscar usuarios con PVG < PV (ERROR)
        cursor.execute("""
            SELECT member_id, first_name, last_name, pv_cache, pvg_cache, (pv_cache - pvg_cache) as difference
            FROM users
            WHERE pvg_cache < pv_cache
            ORDER BY member_id
        """)
        
        errors = cursor.fetchall()
        
        if errors:
            print(f"❌ ERRORES ENCONTRADOS: {len(errors)}\n")
            for error in errors:
                member_id, first_name, last_name, pv, pvg, diff = error
                full_name = f"{first_name} {last_name}"
                print(f"   Member {member_id} ({full_name}):")
                print(f"      PV={pv}, PVG={pvg}")
                print(f"      ⚠️  PVG debería ser >= PV (diferencia: {diff})\n")
        else:
            # Contar total de usuarios
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            print(f"✅ VALIDACIÓN EXITOSA")
            print(f"   Todos los {total_users} usuarios tienen pvg_cache >= pv_cache\n")
        
        print("═══════════════════════════════════════════════════════════════════════════════\n")
        
        cursor.close()
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def show_pvg_examples():
    """Muestra ejemplos de usuarios con su PVG correcto."""
    
    print("\n═══════════════════════════════════════════════════════════════════════════════")
    print("📊 EJEMPLOS DE PVG CORRECTO")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Mostrar primeros 5 usuarios con su PVG
        cursor.execute("""
            SELECT u.member_id, u.first_name, u.last_name, u.pv_cache, u.pvg_cache,
                   (SELECT COUNT(*) FROM usertreepaths WHERE ancestor_id = u.member_id AND depth > 0) as descendants
            FROM users u
            ORDER BY u.member_id
            LIMIT 5
        """)
        
        users = cursor.fetchall()
        
        for user in users:
            member_id, first_name, last_name, pv, pvg, desc_count = user
            full_name = f"{first_name} {last_name}"
            print(f"   Member {member_id} ({full_name}):")
            print(f"      PV personal: {pv}")
            print(f"      PVG total: {pvg}")
            print(f"      Descendientes: {desc_count}")
            print(f"      PV de descendientes: {pvg - pv}\n")
        
        print("═══════════════════════════════════════════════════════════════════════════════\n")
        
        cursor.close()
        
    except Exception as e:
        print(f"\n❌ Error mostrando ejemplos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--verify":
            verify_pvg_calculation()
        elif sys.argv[1] == "--examples":
            show_pvg_examples()
        else:
            print("\n❌ Opción no válida")
            print("\nUso:")
            print("  python3 fix_pvg_cache_direct.py             → Corregir PVG")
            print("  python3 fix_pvg_cache_direct.py --verify    → Solo verificar")
            print("  python3 fix_pvg_cache_direct.py --examples  → Ver ejemplos\n")
    else:
        print("\n⚠️  ADVERTENCIA:")
        print("   Este script modificará la base de datos de producción.")
        print("   ")
        print("   Recalculará el pvg_cache de TODOS los usuarios con la fórmula:")
        print("   PVG = PV_personal + Σ(PV_descendientes)")
        print("   ")
        print("   Opciones:")
        print("   1. python3 fix_pvg_cache_direct.py             → Corregir PVG")
        print("   2. python3 fix_pvg_cache_direct.py --verify    → Solo verificar")
        print("   3. python3 fix_pvg_cache_direct.py --examples  → Ver ejemplos\n")
        
        response = input("¿Deseas continuar con la corrección? (sí/no): ")
        
        if response.lower() in ["sí", "si", "yes", "y", "s"]:
            recalculate_pvg_for_all_users()
            print("\n🔄 Verificando corrección...\n")
            verify_pvg_calculation()
            print("\n📊 Mostrando ejemplos...\n")
            show_pvg_examples()
        else:
            print("\n❌ Operación cancelada por el usuario.\n")
