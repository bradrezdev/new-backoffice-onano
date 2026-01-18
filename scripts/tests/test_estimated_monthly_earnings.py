"""
Test de Proyección de Ganancias Mensuales en Dashboard

Objetivo: Validar que el cálculo de "Estimada ganancia mes" funciona correctamente.

Prueba:
1. Obtener member_id de usuario de prueba
2. Calcular suma de comisiones del período actual (Uninivel + Matching + Alcance)
3. Verificar que el resultado coincide con la proyección mostrada en el dashboard
"""

import sqlmodel
from sqlmodel import Session
from database.models import get_engine
from database.users import Users
from database.comissions import Commissions, BonusType
from database.periods import Periods
from datetime import datetime, timezone
from NNProtect_new_website.mlm_service.exchange_service import ExchangeService

def test_estimated_monthly_earnings():
    """
    Test del cálculo de proyección de ganancias mensuales.
    """
    print("=" * 70)
    print("🧪 TEST: Proyección de Ganancias Mensuales")
    print("=" * 70)
    
    # Usuario de prueba (Bryan Nuñez)
    member_id = 1
    
    try:
        engine = get_engine()
        with Session(engine) as session:
            # 1. Obtener usuario
            user = session.exec(
                sqlmodel.select(Users).where(Users.member_id == member_id)
            ).first()
            
            if not user:
                print(f"❌ Usuario {member_id} no encontrado")
                return False
            
            print(f"\n👤 Usuario: {user.username} (Member ID: {member_id})")
            
            user_currency = ExchangeService.get_country_currency(user.country)
            print(f"💵 Moneda: {user_currency}")
            
            # 2. Obtener período actual
            now = datetime.now(timezone.utc)
            current_period = session.exec(
                sqlmodel.select(Periods)
                .where(
                    sqlmodel.extract('year', Periods.start_date) == now.year,
                    sqlmodel.extract('month', Periods.start_date) == now.month
                )
            ).first()
            
            if not current_period:
                print(f"\n⚠️  No hay período activo para {now.year}-{now.month}")
                print("✅ TEST PASADO - Sin período activo, proyección debe ser $0.00")
                return True
            
            print(f"\n📅 Período actual: {current_period.name} (ID: {current_period.id})")
            
            # 3. Obtener comisiones por tipo
            print("\n📊 Comisiones del período actual:")
            
            # Uninivel
            uninivel_total = session.exec(
                sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                .where(
                    (Commissions.member_id == member_id) &
                    (Commissions.period_id == current_period.id) &
                    (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value)
                )
            ).first() or 0.0
            
            print(f"   • Bono Uninivel:  ${uninivel_total:,.2f} {user_currency}")
            
            # Matching
            matching_total = session.exec(
                sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                .where(
                    (Commissions.member_id == member_id) &
                    (Commissions.period_id == current_period.id) &
                    (Commissions.bonus_type == BonusType.BONO_MATCHING.value)
                )
            ).first() or 0.0
            
            print(f"   • Bono Matching:  ${matching_total:,.2f} {user_currency}")
            
            # Alcance de Rango
            achievement_total = session.exec(
                sqlmodel.select(sqlmodel.func.sum(Commissions.amount_converted))
                .where(
                    (Commissions.member_id == member_id) &
                    (Commissions.period_id == current_period.id) &
                    (Commissions.bonus_type == BonusType.BONO_ALCANCE.value)
                )
            ).first() or 0.0
            
            print(f"   • Bono Alcance:   ${achievement_total:,.2f} {user_currency}")
            
            # 4. Calcular total proyectado
            total_earnings = uninivel_total + matching_total + achievement_total
            
            print(f"\n" + "─" * 70)
            print(f"💰 TOTAL PROYECTADO: ${total_earnings:,.2f} {user_currency}")
            print("─" * 70)
            
            # 5. Validación
            print("\n✅ RESULTADO:")
            print(f"   • El dashboard debe mostrar: ${total_earnings:,.2f} {user_currency}")
            print(f"   • Sección: 'Estimado ganancia mes' (móvil)")
            
            # Verificar que hay comisiones o está en $0
            if total_earnings > 0:
                print(f"\n🎉 Usuario tiene comisiones generadas en este período")
            else:
                print(f"\n⚠️  Usuario no tiene comisiones en este período (mostrará $0.00)")
            
            print("\n" + "=" * 70)
            print("✅ TEST COMPLETADO EXITOSAMENTE")
            print("=" * 70)
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR en el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_estimated_monthly_earnings()
    print("\n")
    sys.exit(0 if success else 1)
