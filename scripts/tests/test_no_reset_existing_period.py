"""
Test para validar que NO se reinician usuarios cuando se intenta crear
un período que ya existe.
"""

import reflex as rx
import sqlmodel
from datetime import datetime, timezone

from database.users import Users, UserStatus
from database.periods import Periods
from database.user_rank_history import UserRankHistory
from NNProtect_new_website.mlm_service.period_service import PeriodService


def test_no_reset_on_existing_period():
    """Valida que no se resetean usuarios al intentar crear período existente."""
    
    print("\n" + "="*80)
    print("🧪 TEST: No resetear usuarios si período ya existe")
    print("="*80 + "\n")
    
    with rx.session() as session:
        
        # Paso 1: Crear un período de prueba
        print("📝 PASO 1: Creando período inicial")
        print("-" * 80)
        
        test_year = 2025
        test_month = 10
        
        # Verificar si ya existe
        test_period_name = f"{test_year}-{test_month:02d}"
        existing = session.exec(
            sqlmodel.select(Periods).where(Periods.name == test_period_name)
        ).first()
        
        if existing:
            print(f"✅ Usando período existente: {test_period_name}")
            period1 = existing
        else:
            # Crear período nuevo
            period1 = PeriodService.create_period_for_month(session, test_year, test_month)
            session.commit()
        
        print(f"✅ Período creado: {period1.name} (ID: {period1.id})")
        
        # Contar registros de user_rank_history iniciales
        initial_rank_count = session.exec(
            sqlmodel.select(sqlmodel.func.count(UserRankHistory.id))
            .where(UserRankHistory.period_id == period1.id)
        ).first()
        
        print(f"✅ Registros de user_rank_history iniciales: {initial_rank_count}")
        
        # Paso 2: Modificar algunos usuarios
        print("\n📝 PASO 2: Modificando usuarios")
        print("-" * 80)
        
        sample_users = session.exec(
            sqlmodel.select(Users).limit(5)
        ).all()
        
        for user in sample_users:
            user.status = UserStatus.QUALIFIED
            user.pv_cache = 5000
            user.pvg_cache = 10000
            user.vn_cache = 6000.00
            session.add(user)
        
        session.commit()
        
        print(f"✅ {len(sample_users)} usuarios modificados")
        print(f"\n{'Member ID':<12} {'Status':<15} {'PV':<8} {'PVG':<8} {'VN':<10}")
        print("-" * 80)
        for user in sample_users:
            session.refresh(user)
            print(
                f"{user.member_id:<12} "
                f"{user.status.value:<15} "
                f"{user.pv_cache:<8} "
                f"{user.pvg_cache:<8} "
                f"{user.vn_cache:<10.2f}"
            )
        
        # Paso 3: Intentar crear el mismo período de nuevo
        print("\n🔧 PASO 3: Intentando crear el mismo período de nuevo")
        print("-" * 80)
        
        period2 = PeriodService.create_period_for_month(session, test_year, test_month)
        session.commit()
        
        print(f"⚠️  Período retornado: {period2.name} (ID: {period2.id})")
        
        # Verificar que es el mismo período
        if period2.id != period1.id:
            print("❌ ERROR: Se creó un nuevo período en lugar de retornar el existente")
            return False
        
        print("✅ Se retornó el período existente (correcto)")
        
        # Paso 4: Validar que los usuarios NO fueron reseteados
        print("\n✅ PASO 4: Validando que usuarios NO fueron reseteados")
        print("-" * 80)
        
        for user in sample_users:
            session.refresh(user)
            
            # Verificar que mantienen sus valores
            if user.status != UserStatus.QUALIFIED:
                print(f"❌ Usuario {user.member_id}: status fue reseteado")
                return False
            
            if user.pv_cache != 5000:
                print(f"❌ Usuario {user.member_id}: pv_cache fue reseteado")
                return False
            
            if user.pvg_cache != 10000:
                print(f"❌ Usuario {user.member_id}: pvg_cache fue reseteado")
                return False
            
            if user.vn_cache != 6000.00:
                print(f"❌ Usuario {user.member_id}: vn_cache fue reseteado")
                return False
        
        print("✅ Usuarios mantienen sus valores (correcto)")
        
        # Mostrar estado final
        print(f"\n{'Member ID':<12} {'Status':<15} {'PV':<8} {'PVG':<8} {'VN':<10}")
        print("-" * 80)
        for user in sample_users:
            print(
                f"{user.member_id:<12} "
                f"{user.status.value:<15} "
                f"{user.pv_cache:<8} "
                f"{user.pvg_cache:<8} "
                f"{user.vn_cache:<10.2f}"
            )
        
        # Paso 5: Validar que NO se duplicaron registros de user_rank_history
        print("\n📈 PASO 5: Validando registros de user_rank_history")
        print("-" * 80)
        
        final_rank_count = session.exec(
            sqlmodel.select(sqlmodel.func.count(UserRankHistory.id))
            .where(UserRankHistory.period_id == period1.id)
        ).first()
        
        if final_rank_count != initial_rank_count:
            print(f"❌ Los registros se duplicaron: {initial_rank_count} → {final_rank_count}")
            return False
        
        print(f"✅ Registros sin duplicar: {final_rank_count} (correcto)")
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETADO: No se resetean usuarios en período existente")
        print("="*80 + "\n")
        
        return True


if __name__ == "__main__":
    try:
        success = test_no_reset_on_existing_period()
        
        if success:
            print("🎉 Test completado exitosamente")
            exit(0)
        else:
            print("❌ Test falló")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
