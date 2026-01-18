"""
Crea una pequeña red de prueba para validar que se asignen
period_id y referral_link correctamente.
"""

import reflex as rx
import sqlmodel
from datetime import datetime, timezone

from database.users import Users
from database.user_rank_history import UserRankHistory
from database.periods import Periods


def test_create_small_network():
    """Crea una red pequeña 2x2 con 2 niveles."""
    
    print("\n" + "="*80)
    print("🧪 TEST: Crear red pequeña y validar datos")
    print("="*80 + "\n")
    
    try:
        # Importar AdminState
        import sys
        sys.path.insert(0, '/Users/bradrez/Documents/NNProtect_new_website')
        
        from NNProtect_new_website.Admin_app.admin_state import AdminState
        
        # Crear instancia del estado
        admin = AdminState()
        
        print("📝 PASO 1: Configurando red de prueba")
        print("-" * 80)
        print("  • Sponsor raíz: Member ID 1")
        print("  • Estructura: 2x2")
        print("  • Profundidad: 2 niveles")
        print("  • País: México")
        print("  • Crear órdenes: No")
        
        # Configurar parámetros
        admin.network_root_member_id = "1"
        admin.network_structure = "2x2"
        admin.network_depth = "2"
        admin.network_country = "México"
        admin.network_create_orders = False
        
        # Calcular estimaciones
        structure = 2
        depth = 2
        estimated_users = sum(structure ** level for level in range(1, depth + 1))
        
        print(f"\n  ✅ Se crearán aproximadamente {estimated_users} usuarios")
        
        print("\n🚀 PASO 2: Ejecutando creación de red")
        print("-" * 80)
        
        # Ejecutar creación
        admin.create_network_tree()
        
        print("\n✅ PASO 3: Validando usuarios creados")
        print("-" * 80)
        
        with rx.session() as session:
            # Obtener período actual
            from NNProtect_new_website.mlm_service.period_service import PeriodService
            current_period = PeriodService.get_current_period(session)
            
            if not current_period:
                print("❌ No hay período actual")
                return False
            
            print(f"  • Período actual: {current_period.name} (ID: {current_period.id})")
            
            # Obtener los últimos N usuarios creados
            latest_users = session.exec(
                sqlmodel.select(Users)
                .where(Users.first_name.like("Test%"))
                .order_by(Users.member_id.desc())
                .limit(estimated_users)
            ).all()
            
            if not latest_users:
                print("❌ No se encontraron usuarios recién creados")
                return False
            
            print(f"  • Usuarios encontrados: {len(latest_users)}")
            
            # Validar cada usuario
            print(f"\n{'Member ID':<12} {'Referral Link':<45} {'Period ID':<12} {'Status':<10}")
            print("-" * 80)
            
            all_valid = True
            
            for user in reversed(latest_users[:6]):  # Mostrar primeros 6
                # Validar referral_link
                expected_link = f"https://nnprotect.com/ref/{user.member_id}"
                has_referral = user.referral_link == expected_link
                
                # Obtener registro de rango
                rank_record = session.exec(
                    sqlmodel.select(UserRankHistory)
                    .where(UserRankHistory.member_id == user.member_id)
                    .order_by(UserRankHistory.achieved_on.desc())
                ).first()
                
                has_period = rank_record and rank_record.period_id == current_period.id
                
                status = "✅" if (has_referral and has_period) else "❌"
                
                print(
                    f"{user.member_id:<12} "
                    f"{user.referral_link or 'N/A':<45} "
                    f"{rank_record.period_id if rank_record else 'N/A':<12} "
                    f"{status:<10}"
                )
                
                if not has_referral:
                    print(f"  ⚠️  Referral link incorrecto")
                    all_valid = False
                
                if not has_period:
                    print(f"  ⚠️  Period ID no asignado o incorrecto")
                    all_valid = False
            
            if all_valid:
                print("\n" + "="*80)
                print("✅ TODOS LOS USUARIOS TIENEN LOS DATOS CORRECTOS")
                print("="*80)
                return True
            else:
                print("\n" + "="*80)
                print("❌ ALGUNOS USUARIOS NO TIENEN LOS DATOS CORRECTOS")
                print("="*80)
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_create_small_network()
    
    if success:
        print("\n🎉 Test completado exitosamente")
        exit(0)
    else:
        print("\n❌ Test falló")
        exit(1)
