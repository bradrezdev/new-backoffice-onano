"""
Test para validar el reinicio de usuarios al crear un nuevo período.

Prueba:
1. Estado inicial de usuarios
2. Creación de nuevo período
3. Validación de reseteo de datos
"""

import reflex as rx
import sqlmodel
from datetime import datetime, timezone

from database.users import Users, UserStatus
from database.periods import Periods
from database.user_rank_history import UserRankHistory
from NNProtect_new_website.mlm_service.period_service import PeriodService


def test_period_reset():
    """Prueba completa del reinicio de usuarios al crear nuevo período."""
    
    print("\n" + "="*80)
    print("🧪 TEST: Reinicio de usuarios al crear nuevo período")
    print("="*80 + "\n")
    
    with rx.session() as session:
        
        # Paso 1: Mostrar estado inicial de algunos usuarios
        print("📊 PASO 1: Estado inicial de usuarios")
        print("-" * 80)
        
        sample_users = session.exec(
            sqlmodel.select(Users).limit(5)
        ).all()
        
        if not sample_users:
            print("❌ No hay usuarios en la base de datos")
            return False
        
        print(f"{'Member ID':<12} {'Status':<15} {'PV':<8} {'PVG':<8} {'VN':<10}")
        print("-" * 80)
        for user in sample_users:
            print(
                f"{user.member_id:<12} "
                f"{user.status.value:<15} "
                f"{user.pv_cache:<8} "
                f"{user.pvg_cache:<8} "
                f"{user.vn_cache:<10.2f}"
            )
        
        # Paso 2: Modificar algunos usuarios para simular actividad
        print("\n📝 PASO 2: Simulando actividad de usuarios")
        print("-" * 80)
        
        for user in sample_users[:3]:
            user.status = UserStatus.QUALIFIED
            user.pv_cache = 2000
            user.pvg_cache = 5000
            user.vn_cache = 2500.50
            session.add(user)
        
        session.commit()
        print("✅ 3 usuarios modificados con datos simulados")
        
        # Mostrar usuarios modificados
        print(f"\n{'Member ID':<12} {'Status':<15} {'PV':<8} {'PVG':<8} {'VN':<10}")
        print("-" * 80)
        for user in sample_users[:3]:
            session.refresh(user)
            print(
                f"{user.member_id:<12} "
                f"{user.status.value:<15} "
                f"{user.pv_cache:<8} "
                f"{user.pvg_cache:<8} "
                f"{user.vn_cache:<10.2f}"
            )
        
        # Paso 3: Crear nuevo período (esto debe resetear usuarios)
        print("\n🆕 PASO 3: Creando nuevo período de prueba")
        print("-" * 80)
        
        # Usar un mes único para el test
        now = datetime.now(timezone.utc)
        test_year = now.year
        test_month = 1  # Enero del próximo ciclo
        
        # Verificar si existe
        test_period_name = f"{test_year}-{test_month:02d}"
        existing_test_period = session.exec(
            sqlmodel.select(Periods).where(Periods.name == test_period_name)
        ).first()
        
        if existing_test_period:
            print(f"✅ Usando período existente: {test_period_name}")
            new_period = existing_test_period
        else:
            # Crear nuevo período (esto debe ejecutar el reset automáticamente)
            print(f"🆕 Creando nuevo período: {test_period_name}")
            new_period = PeriodService.create_period_for_month(session, test_year, test_month)
        
        if not new_period:
            print("❌ No se pudo crear el período")
            return False
        
        session.commit()
        
        # Paso 4: Validar que los usuarios fueron reseteados
        print("\n✅ PASO 4: Validando reseteo de usuarios")
        print("-" * 80)
        
        all_users = session.exec(sqlmodel.select(Users)).all()
        
        errors = []
        
        for user in all_users:
            session.refresh(user)
            
            # Validar status
            if user.status != UserStatus.NO_QUALIFIED:
                errors.append(f"Usuario {user.member_id}: status = {user.status.value} (esperado: NO_QUALIFIED)")
            
            # Validar pv_cache
            if user.pv_cache != 0:
                errors.append(f"Usuario {user.member_id}: pv_cache = {user.pv_cache} (esperado: 0)")
            
            # Validar pvg_cache
            if user.pvg_cache != 0:
                errors.append(f"Usuario {user.member_id}: pvg_cache = {user.pvg_cache} (esperado: 0)")
            
            # Validar vn_cache
            if user.vn_cache != 0.0:
                errors.append(f"Usuario {user.member_id}: vn_cache = {user.vn_cache} (esperado: 0.0)")
        
        if errors:
            print("❌ ERRORES ENCONTRADOS:")
            for error in errors:
                print(f"   • {error}")
            return False
        
        print(f"✅ {len(all_users)} usuarios reseteados correctamente")
        
        # Mostrar estado final de los usuarios de muestra
        print(f"\n{'Member ID':<12} {'Status':<15} {'PV':<8} {'PVG':<8} {'VN':<10}")
        print("-" * 80)
        for user in sample_users[:3]:
            session.refresh(user)
            print(
                f"{user.member_id:<12} "
                f"{user.status.value:<15} "
                f"{user.pv_cache:<8} "
                f"{user.pvg_cache:<8} "
                f"{user.vn_cache:<10.2f}"
            )
        
        # Paso 5: Validar registros de user_rank_history
        print("\n📈 PASO 5: Validando registros de user_rank_history")
        print("-" * 80)
        
        rank_records = session.exec(
            sqlmodel.select(UserRankHistory)
            .where(UserRankHistory.period_id == new_period.id)
        ).all()
        
        if len(rank_records) != len(all_users):
            print(f"❌ Número incorrecto de registros: {len(rank_records)} (esperado: {len(all_users)})")
            return False
        
        print(f"✅ {len(rank_records)} registros de rango creados")
        
        # Validar que todos tengan rank_id = 1
        wrong_ranks = [r for r in rank_records if r.rank_id != 1]
        if wrong_ranks:
            print(f"❌ {len(wrong_ranks)} registros con rank_id incorrecto")
            for r in wrong_ranks[:5]:
                print(f"   • Member {r.member_id}: rank_id = {r.rank_id} (esperado: 1)")
            return False
        
        print("✅ Todos los registros tienen rank_id = 1")
        
        # Mostrar algunos registros de muestra
        print(f"\n{'Member ID':<12} {'Rank ID':<10} {'Period ID':<12}")
        print("-" * 80)
        for record in rank_records[:5]:
            print(f"{record.member_id:<12} {record.rank_id:<10} {record.period_id:<12}")
        
        print("\n" + "="*80)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("="*80 + "\n")
        
        return True


if __name__ == "__main__":
    try:
        success = test_period_reset()
        
        if success:
            print("🎉 Test completado exitosamente")
            exit(0)
        else:
            print("❌ Test falló")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL TEST: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
