"""
═══════════════════════════════════════════════════════════════════════════════
🔧 SCRIPT DE CORRECCIÓN: Recalcular PVG_CACHE para todos los usuarios
═══════════════════════════════════════════════════════════════════════════════

PROBLEMA:
El bug en admin_state.py causó que pvg_cache no incluyera el pv_cache del usuario.

SOLUCIÓN:
Recalcular pvg_cache para TODOS los usuarios con la fórmula correcta:
PVG = PV_personal + Σ(PV_descendientes)

AUTOR: Arquitecto de Datos
FECHA: 31 de octubre de 2025
"""

import sqlmodel
from database.users import Users
from database.usertreepaths import UserTreePath
import os

def recalculate_pvg_for_all_users():
    """
    Recalcula el pvg_cache para todos los usuarios.
    
    Algoritmo:
    1. Para cada usuario, obtener su pv_cache
    2. Obtener todos sus descendientes
    3. Sumar el pv_cache de todos los descendientes
    4. PVG = PV_personal + Σ(PV_descendientes)
    """
    
    print("\n═══════════════════════════════════════════════════════════════════════════════")
    print("🔧 RECALCULANDO PVG_CACHE PARA TODOS LOS USUARIOS")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    # Conectar a base de datos
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("❌ Error: DATABASE_URL no está configurada")
        return
    
    engine = sqlmodel.create_engine(db_url, echo=False)
    
    with sqlmodel.Session(engine) as session:
        
        # Obtener TODOS los usuarios
        all_users = session.exec(sqlmodel.select(Users)).all()
        
        print(f"📊 Total de usuarios a procesar: {len(all_users)}\n")
        
        corrections_made = 0
        users_correct = 0
        
        for user in all_users:
            # 1. El PVG mínimo es el PV del usuario
            expected_pvg = user.pv_cache
            
            # 2. Obtener todos los descendientes
            descendant_paths = session.exec(
                sqlmodel.select(UserTreePath)
                .where(UserTreePath.ancestor_id == user.member_id)
                .where(UserTreePath.depth > 0)
            ).all()
            
            # 3. Sumar el PV de todos los descendientes
            for path in descendant_paths:
                descendant = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == path.descendant_id)
                ).first()
                
                if descendant:
                    expected_pvg += descendant.pv_cache
            
            # 4. Comparar con el pvg_cache actual
            if user.pvg_cache != expected_pvg:
                print(f"   ❌ Member {user.member_id} ({user.full_name}):")
                print(f"      PVG actual: {user.pvg_cache}")
                print(f"      PVG esperado: {expected_pvg}")
                print(f"      Diferencia: {expected_pvg - user.pvg_cache}")
                
                # Corregir
                user.pvg_cache = expected_pvg
                session.add(user)
                corrections_made += 1
            else:
                users_correct += 1
        
        # Guardar cambios
        session.commit()
        
        print(f"\n═══════════════════════════════════════════════════════════════════════════════")
        print(f"✅ CORRECCIÓN COMPLETADA")
        print(f"═══════════════════════════════════════════════════════════════════════════════\n")
        print(f"   📊 Total usuarios: {len(all_users)}")
        print(f"   ✅ Usuarios correctos: {users_correct}")
        print(f"   🔧 Correcciones realizadas: {corrections_made}")
        print(f"\n═══════════════════════════════════════════════════════════════════════════════\n")

def verify_pvg_calculation():
    """
    Verifica que todos los usuarios tengan pvg_cache >= pv_cache.
    Esta es una validación rápida post-corrección.
    """
    
    print("\n═══════════════════════════════════════════════════════════════════════════════")
    print("🔍 VERIFICANDO CÁLCULO DE PVG")
    print("═══════════════════════════════════════════════════════════════════════════════\n")
    
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("❌ Error: DATABASE_URL no está configurada")
        return
    
    engine = sqlmodel.create_engine(db_url, echo=False)
    
    with sqlmodel.Session(engine) as session:
        all_users = session.exec(sqlmodel.select(Users)).all()
        
        errors = []
        
        for user in all_users:
            if user.pvg_cache < user.pv_cache:
                errors.append({
                    "member_id": user.member_id,
                    "full_name": user.full_name,
                    "pv_cache": user.pv_cache,
                    "pvg_cache": user.pvg_cache,
                    "difference": user.pv_cache - user.pvg_cache
                })
        
        if errors:
            print(f"❌ ERRORES ENCONTRADOS: {len(errors)}\n")
            for error in errors:
                print(f"   Member {error['member_id']} ({error['full_name']}):")
                print(f"      PV={error['pv_cache']}, PVG={error['pvg_cache']}")
                print(f"      ⚠️  PVG debería ser >= PV (diferencia: {error['difference']})\n")
        else:
            print(f"✅ VALIDACIÓN EXITOSA")
            print(f"   Todos los {len(all_users)} usuarios tienen pvg_cache >= pv_cache\n")
        
        print("═══════════════════════════════════════════════════════════════════════════════\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_pvg_calculation()
    else:
        print("\n⚠️  ADVERTENCIA:")
        print("   Este script modificará la base de datos de producción.")
        print("   ")
        print("   Opciones:")
        print("   1. python fix_pvg_cache.py          → Corregir PVG de todos los usuarios")
        print("   2. python fix_pvg_cache.py --verify → Solo verificar (no modifica)\n")
        
        response = input("¿Deseas continuar con la corrección? (sí/no): ")
        
        if response.lower() in ["sí", "si", "yes", "y", "s"]:
            recalculate_pvg_for_all_users()
            print("\n🔄 Verificando corrección...\n")
            verify_pvg_calculation()
        else:
            print("\n❌ Operación cancelada por el usuario.\n")
