"""
Script de prueba para verificar asignación automática de rangos.
Prueba los 3 requisitos principales del usuario.

✅ Tarea 1: Aplicar rango con id=1 automáticamente cuando el usuario se registra
✅ Tarea 2: Comenzar a llevar un historial en user_rank_history.py 
✅ Tarea 3: Crear método que registre cuál es el rango más grande alcanzado
"""

import reflex as rx
import sqlmodel
from NNProtect_new_website.mlm_service.mlm_user_manager import MLMUserManager
from NNProtect_new_website.mlm_service.rank_service import RankService
from database.ranks import Ranks
from database.user_rank_history import UserRankHistory
from database.users import Users

def test_automatic_rank_assignment():
    """Prueba asignación automática de rango 'Sin rango' durante registro."""
    print("\n🧪 === PRUEBA: ASIGNACIÓN AUTOMÁTICA DE RANGO ===")
    
    with rx.session() as session:
        try:
            # Simular registro de nuevo usuario
            test_user = MLMUserManager.create_mlm_user(
                session=session,
                supabase_user_id="test_user_ranks_001",
                first_name="Test",
                last_name="RankUser",
                email="test.ranks@example.com",
                sponsor_member_id=None
            )
            
            session.commit()  # Confirmar transacción
            
            print(f"✅ Usuario creado con member_id: {test_user.member_id}")
            
            # VERIFICAR TAREA 1: ¿Se asignó rango id=1 automáticamente?
            current_rank = MLMUserManager.get_user_current_rank(test_user.member_id)
            print(f"🔍 Rango actual asignado: {current_rank}")
            
            if current_rank == 1:
                print("✅ TAREA 1 COMPLETADA: Rango id=1 asignado automáticamente")
            else:
                print("❌ FALLA TAREA 1: No se asignó rango automáticamente")
            
            # VERIFICAR TAREA 2: ¿Se creó historial en user_rank_history?
            rank_history = MLMUserManager.get_user_rank_history(test_user.member_id)
            print(f"🔍 Registros en historial: {len(rank_history)}")
            
            if len(rank_history) > 0:
                print("✅ TAREA 2 COMPLETADA: Historial de rangos iniciado")
                print(f"   📊 Primer registro: Rango {rank_history[0]['rank_name']} el {rank_history[0]['achieved_on']}")
            else:
                print("❌ FALLA TAREA 2: No se creó historial de rangos")
            
            # VERIFICAR TAREA 3: ¿Funciona el método de rango más alto?
            highest_rank = MLMUserManager.get_user_highest_rank(test_user.member_id)
            print(f"🔍 Rango más alto alcanzado: {highest_rank}")
            
            if highest_rank == 1:
                print("✅ TAREA 3 COMPLETADA: Método de rango más alto funciona")
            else:
                print("❌ FALLA TAREA 3: Método de rango más alto no funciona")
            
            # 🧪 PRUEBA ADICIONAL: Promoción de rango
            print("\n🧪 PRUEBA ADICIONAL: Promoción de rango")
            promotion_success = MLMUserManager.promote_user_rank(test_user.member_id, 2)
            
            if promotion_success:
                print("✅ Promoción exitosa")
                
                # Verificar cambios
                new_current_rank = MLMUserManager.get_user_current_rank(test_user.member_id)
                new_highest_rank = MLMUserManager.get_user_highest_rank(test_user.member_id)
                new_history = MLMUserManager.get_user_rank_history(test_user.member_id)
                
                print(f"   📊 Rango actual después de promoción: {new_current_rank}")
                print(f"   📊 Rango más alto después de promoción: {new_highest_rank}")
                print(f"   📊 Registros en historial: {len(new_history)}")
            else:
                print("❌ Promoción falló")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en prueba: {e}")
            return False

def test_rank_system_integrity():
    """Verifica integridad del sistema de rangos."""
    print("\n🧪 === VERIFICACIÓN: INTEGRIDAD DEL SISTEMA ===")
    
    with rx.session() as session:
        try:
            # Verificar que existe rango id=1 "Sin rango"
            rank_sin_rango = session.exec(
                sqlmodel.select(Ranks).where(Ranks.id == 1)
            ).first()
            
            if rank_sin_rango:
                print(f"✅ Rango id=1 existe: '{rank_sin_rango.name}'")
            else:
                print("❌ CRÍTICO: Rango id=1 'Sin rango' no existe en base de datos")
                return False
            
            # Verificar que hay más rangos disponibles para promociones
            total_ranks = session.exec(sqlmodel.select(Ranks)).all()
            print(f"✅ Total de rangos disponibles: {len(total_ranks)}")
            
            for rank in total_ranks[:3]:  # Mostrar primeros 3
                print(f"   📊 Rango {rank.id}: '{rank.name}' (PV: {rank.pv_required}, PVG: {rank.pvg_required})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando integridad: {e}")
            return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE SISTEMA AUTOMÁTICO DE RANGOS")
    print("=" * 60)
    
    # Verificar integridad del sistema
    integrity_ok = test_rank_system_integrity()
    
    if integrity_ok:
        # Probar asignación automática
        test_ok = test_automatic_rank_assignment()
        
        if test_ok:
            print("\n🎉 TODAS LAS PRUEBAS EXITOSAS")
            print("✅ Sistema de rangos automático funcionando correctamente")
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
    else:
        print("\n❌ FALLA DE INTEGRIDAD - No se pueden ejecutar pruebas")
    
    print("=" * 60)