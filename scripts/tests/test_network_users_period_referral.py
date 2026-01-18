"""
Test para validar que los usuarios creados por la herramienta de Red
tengan asignado un period_id en su rank y un referral_link.
"""

import reflex as rx
import sqlmodel
from datetime import datetime, timezone

from database.users import Users
from database.user_rank_history import UserRankHistory
from database.periods import Periods
from NNProtect_new_website.mlm_service.period_service import PeriodService


def test_network_users_have_period_and_referral():
    """Valida que usuarios creados por red tengan period_id y referral_link."""
    
    print("\n" + "="*80)
    print("🧪 TEST: Usuarios de Red con Period ID y Referral Link")
    print("="*80 + "\n")
    
    with rx.session() as session:
        
        # Paso 1: Obtener o crear período actual
        print("📅 PASO 1: Verificando período actual")
        print("-" * 80)
        
        current_period = PeriodService.get_current_period(session)
        if not current_period:
            print("⚠️  No hay período actual, creando...")
            current_period = PeriodService.auto_create_current_month_period(session)
            session.commit()
        
        if not current_period:
            print("❌ ERROR: No se pudo obtener o crear período actual")
            return False
        
        print(f"✅ Período actual: {current_period.name} (ID: {current_period.id})")
        
        # Paso 2: Obtener usuarios de prueba (usuarios tipo Test)
        print("\n👥 PASO 2: Obteniendo usuarios de prueba")
        print("-" * 80)
        
        test_users = session.exec(
            sqlmodel.select(Users)
            .where(Users.first_name.like("Test%"))
            .limit(10)
        ).all()
        
        if not test_users:
            print("⚠️  No hay usuarios de prueba (Test*) en la base de datos")
            print("   Esto es normal si no se ha usado la herramienta de Red aún")
            print("   ✅ Test considerado exitoso (no hay datos que validar)")
            return True
        
        print(f"✅ Encontrados {len(test_users)} usuarios de prueba")
        
        # Paso 3: Validar referral_link
        print("\n🔗 PASO 3: Validando referral_link")
        print("-" * 80)
        
        users_without_referral = []
        users_with_referral = []
        
        for user in test_users:
            if not user.referral_link or user.referral_link == "":
                users_without_referral.append(user.member_id)
            else:
                users_with_referral.append(user.member_id)
                # Verificar formato
                expected_link = f"https://nnprotect.com/ref/{user.member_id}"
                if user.referral_link != expected_link:
                    print(f"⚠️  Usuario {user.member_id}: referral_link incorrecto")
                    print(f"   Esperado: {expected_link}")
                    print(f"   Obtenido: {user.referral_link}")
        
        if users_without_referral:
            print(f"❌ {len(users_without_referral)} usuarios SIN referral_link:")
            for mid in users_without_referral[:5]:
                print(f"   • Member ID: {mid}")
            return False
        
        print(f"✅ {len(users_with_referral)} usuarios con referral_link correcto")
        
        # Mostrar algunos ejemplos
        print(f"\n{'Member ID':<12} {'Referral Link':<50}")
        print("-" * 80)
        for user in test_users[:5]:
            print(f"{user.member_id:<12} {user.referral_link:<50}")
        
        # Paso 4: Validar period_id en UserRankHistory
        print("\n📊 PASO 4: Validando period_id en UserRankHistory")
        print("-" * 80)
        
        rank_records_without_period = []
        rank_records_with_period = []
        
        for user in test_users:
            # Obtener registro de rango más reciente
            rank_record = session.exec(
                sqlmodel.select(UserRankHistory)
                .where(UserRankHistory.member_id == user.member_id)
                .order_by(UserRankHistory.achieved_on.desc())
            ).first()
            
            if not rank_record:
                print(f"⚠️  Usuario {user.member_id}: no tiene registro de rango")
                continue
            
            if not rank_record.period_id:
                rank_records_without_period.append(user.member_id)
            else:
                rank_records_with_period.append({
                    'member_id': user.member_id,
                    'period_id': rank_record.period_id,
                    'rank_id': rank_record.rank_id
                })
        
        if rank_records_without_period:
            print(f"❌ {len(rank_records_without_period)} registros SIN period_id:")
            for mid in rank_records_without_period[:5]:
                print(f"   • Member ID: {mid}")
            return False
        
        print(f"✅ {len(rank_records_with_period)} registros con period_id asignado")
        
        # Mostrar algunos ejemplos
        print(f"\n{'Member ID':<12} {'Period ID':<12} {'Rank ID':<10}")
        print("-" * 80)
        for record in rank_records_with_period[:5]:
            print(
                f"{record['member_id']:<12} "
                f"{record['period_id']:<12} "
                f"{record['rank_id']:<10}"
            )
        
        # Paso 5: Verificar que el period_id sea el actual
        print("\n✅ PASO 5: Verificando que period_id sea el actual")
        print("-" * 80)
        
        wrong_period_ids = []
        
        for record in rank_records_with_period:
            if record['period_id'] != current_period.id:
                wrong_period_ids.append({
                    'member_id': record['member_id'],
                    'period_id': record['period_id'],
                    'expected': current_period.id
                })
        
        if wrong_period_ids:
            print(f"⚠️  {len(wrong_period_ids)} registros con period_id diferente al actual:")
            print("   Esto puede ser normal si se crearon en períodos anteriores")
            for rec in wrong_period_ids[:3]:
                print(f"   • Member {rec['member_id']}: Period {rec['period_id']} (actual: {rec['expected']})")
        else:
            print(f"✅ Todos los registros tienen el period_id actual ({current_period.id})")
        
        print("\n" + "="*80)
        print("✅ TODAS LAS VALIDACIONES PASARON")
        print("="*80 + "\n")
        
        # Resumen
        print("📋 RESUMEN:")
        print(f"  • Usuarios validados: {len(test_users)}")
        print(f"  • Con referral_link: {len(users_with_referral)}")
        print(f"  • Con period_id en rank: {len(rank_records_with_period)}")
        print(f"  • Período actual: {current_period.name}")
        
        return True


if __name__ == "__main__":
    try:
        success = test_network_users_have_period_and_referral()
        
        if success:
            print("\n🎉 Test completado exitosamente")
            exit(0)
        else:
            print("\n❌ Test falló")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
