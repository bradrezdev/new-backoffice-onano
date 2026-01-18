"""
Test para validar el reinicio de usuarios desde el admin panel.

Simula el flujo de cierre de período desde el panel de administración.
"""

import reflex as rx
import sqlmodel
from datetime import datetime, timezone

from database.users import Users, UserStatus
from database.periods import Periods
from database.user_rank_history import UserRankHistory


def test_admin_period_creation():
    """Prueba el flujo de creación de período desde admin (simulado)."""
    
    print("\n" + "="*80)
    print("🧪 TEST: Creación de período desde Admin Panel (simulado)")
    print("="*80 + "\n")
    
    with rx.session() as session:
        
        # Paso 1: Modificar algunos usuarios para simular actividad
        print("📝 PASO 1: Simulando actividad de usuarios")
        print("-" * 80)
        
        sample_users = session.exec(
            sqlmodel.select(Users).limit(5)
        ).all()
        
        for user in sample_users:
            user.status = UserStatus.QUALIFIED
            user.pv_cache = 3500
            user.pvg_cache = 8000
            user.vn_cache = 4200.75
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
        
        # Paso 2: Simular creación de período desde admin
        print("\n🔧 PASO 2: Simulando creación de período desde Admin")
        print("-" * 80)
        
        now = datetime.now(timezone.utc)
        next_month = 11  # Mes de prueba diferente
        next_year = 2025
        
        new_period_name = f"{next_year}-{next_month:02d}"
        
        # Verificar si ya existe
        existing_period = session.exec(
            sqlmodel.select(Periods).where(Periods.name == new_period_name)
        ).first()
        
        if existing_period:
            print(f"⚠️  Eliminando período de prueba existente: {new_period_name}")
            # Eliminar registros de user_rank_history asociados
            old_rank_records = session.exec(
                sqlmodel.select(UserRankHistory)
                .where(UserRankHistory.period_id == existing_period.id)
            ).all()
            for record in old_rank_records:
                session.delete(record)
            session.delete(existing_period)
            session.commit()
        
        # Crear período (simulando el código del admin)
        new_period = Periods(
            name=new_period_name,
            description=f"Período {new_period_name}",
            starts_on=now,
            ends_on=datetime(next_year, next_month, 28, 23, 59, 59, tzinfo=timezone.utc)
        )
        
        session.add(new_period)
        session.flush()
        
        print(f"✨ Nuevo período creado: {new_period.name} (ID: {new_period.id})")
        
        # Reiniciar usuarios (como lo hace el admin)
        from NNProtect_new_website.mlm_service.period_service import PeriodService
        PeriodService.reset_users_for_new_period(session, new_period)
        
        session.commit()
        
        # Paso 3: Validar reseteo
        print("\n✅ PASO 3: Validando reseteo de usuarios")
        print("-" * 80)
        
        all_users = session.exec(sqlmodel.select(Users)).all()
        
        errors = []
        for user in all_users:
            session.refresh(user)
            
            if user.status != UserStatus.NO_QUALIFIED:
                errors.append(f"Usuario {user.member_id}: status incorrecto")
            if user.pv_cache != 0:
                errors.append(f"Usuario {user.member_id}: pv_cache incorrecto")
            if user.pvg_cache != 0:
                errors.append(f"Usuario {user.member_id}: pvg_cache incorrecto")
            if user.vn_cache != 0.0:
                errors.append(f"Usuario {user.member_id}: vn_cache incorrecto")
        
        if errors:
            print("❌ ERRORES:")
            for error in errors[:10]:
                print(f"   • {error}")
            return False
        
        print(f"✅ {len(all_users)} usuarios reseteados correctamente")
        
        # Mostrar usuarios de muestra
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
        
        # Paso 4: Validar user_rank_history
        print("\n📈 PASO 4: Validando registros de user_rank_history")
        print("-" * 80)
        
        rank_records = session.exec(
            sqlmodel.select(UserRankHistory)
            .where(UserRankHistory.period_id == new_period.id)
        ).all()
        
        if len(rank_records) != len(all_users):
            print(f"❌ Número incorrecto de registros")
            return False
        
        wrong_ranks = [r for r in rank_records if r.rank_id != 1]
        if wrong_ranks:
            print(f"❌ {len(wrong_ranks)} registros con rank_id incorrecto")
            return False
        
        print(f"✅ {len(rank_records)} registros de rango creados con rank_id=1")
        
        print("\n" + "="*80)
        print("✅ TEST DE ADMIN PANEL COMPLETADO EXITOSAMENTE")
        print("="*80 + "\n")
        
        return True


if __name__ == "__main__":
    try:
        success = test_admin_period_creation()
        
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
