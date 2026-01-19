"""
Job programado de cierre mensual.
Se ejecuta el último día del mes a las 23:59:59 (horario México Central).
Calcula todas las comisiones mensuales (Uninivel, Matching, etc).

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import reflex as rx
import sqlmodel
from typing import List, Optional
from datetime import datetime, timezone

from database.users import Users
from database.periods import Periods
from NNProtect_new_website.modules.network.backend.commission_service import CommissionService
from NNProtect_new_website.utils.timezone_mx import get_mexico_now


class MonthlyClosureJob:
    """
    Job de cierre mensual para cálculo de comisiones recurrentes.
    Principio POO: Encapsula toda la lógica del cierre mensual.
    """

    @classmethod
    def execute_monthly_closure(cls) -> bool:
        """
        Ejecuta el cierre mensual completo.
        SIMPLIFICADO: Solo paga comisiones PENDING y resetea usuarios.

        Pasos:
        1. Verificar que no se haya ejecutado ya (idempotencia)
        2. Obtener período actual
        3. Pagar todas las comisiones PENDING
        4. Cerrar período
        5. Crear nuevo período
        6. Resetear todos los usuarios

        Returns:
            True si el cierre fue exitoso, False si falló
        """
        try:
            from database.comissions import Commissions, CommissionStatus
            from NNProtect_new_website.modules.finance.backend.wallet_service import WalletService
            from NNProtect_new_website.modules.network.backend.period_reset_service import PeriodResetService
            
            print("\n" + "="*80)
            print("🔄 INICIANDO CIERRE MENSUAL AUTOMÁTICO")
            print("="*80 + "\n")

            with rx.session() as session:
                # 1. Obtener período actual
                current_period = cls._get_current_period(session)

                if not current_period:
                    print("❌ No hay período activo para cerrar")
                    return False

                # 2. Verificar idempotencia (no ejecutar si ya está cerrado)
                if current_period.closed_at is not None:
                    print(f"⚠️  Período {current_period.name} ya está cerrado")
                    return True

                print(f"📅 Período actual: {current_period.name} (ID: {current_period.id})")

                # 3. Obtener todas las comisiones PENDING del período
                pending_commissions = session.exec(
                    sqlmodel.select(Commissions)
                    .where(
                        (Commissions.period_id == current_period.id) &
                        (Commissions.status == CommissionStatus.PENDING.value)
                    )
                ).all()

                print(f"💸 Comisiones PENDING encontradas: {len(pending_commissions)}\n")

                # 4. Depositar cada comisión en la wallet del usuario
                deposited_count = 0
                deposited_total = 0.0
                failed_count = 0

                for commission in pending_commissions:
                    if commission.id is None:
                        failed_count += 1
                        continue

                    success = WalletService.deposit_commission(
                        session=session,
                        member_id=commission.member_id,
                        commission_id=commission.id,
                        amount=commission.amount_converted,
                        currency=commission.currency_destination,
                        description=commission.notes
                    )

                    if success:
                        deposited_count += 1
                        deposited_total += commission.amount_converted
                    else:
                        failed_count += 1

                print(f"\n💰 RESUMEN DE DEPÓSITOS:")
                print(f"   ✅ Exitosos: {deposited_count}")
                print(f"   ❌ Fallidos: {failed_count}")
                print(f"   💵 Total depositado: ${deposited_total:.2f}\n")

                # 5. Cerrar el período actual
                current_period.closed_at = datetime.now(timezone.utc)
                session.add(current_period)

                print(f"🔒 Período {current_period.name} cerrado exitosamente\n")

                # 6. Crear nuevo período
                now = datetime.now(timezone.utc)
                next_month = now.month + 1 if now.month < 12 else 1
                next_year = now.year if now.month < 12 else now.year + 1

                new_period_name = f"{next_year}-{next_month:02d}"

                # Verificar si ya existe el período
                existing_period = session.exec(
                    sqlmodel.select(Periods).where(Periods.name == new_period_name)
                ).first()

                if existing_period:
                    print(f"⚠️  Período {new_period_name} ya existe (ID: {existing_period.id})")
                    new_period = existing_period
                else:
                    new_period = Periods(
                        name=new_period_name,
                        description=f"Período {new_period_name}",
                        starts_on=now,
                        ends_on=datetime(next_year, next_month, 28, 23, 59, 59, tzinfo=timezone.utc)
                    )

                    session.add(new_period)
                    session.flush()

                    print(f"✨ Nuevo período creado: {new_period.name} (ID: {new_period.id})")

                    # 7. Resetear TODOS los usuarios para el nuevo período
                    if new_period.id:
                        users_reset = PeriodResetService.reset_all_users_for_new_period(
                            session, new_period.id
                        )
                        print(f"🔄 {users_reset} usuarios reseteados para el nuevo período")

                session.commit()

                print("\n" + "="*80)
                print("✅ CIERRE MENSUAL COMPLETADO")
                print("="*80 + "\n")

                return True

        except Exception as e:
            print(f"❌ Error en cierre mensual: {e}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def _get_current_period(cls, session) -> Optional[Periods]:
        """
        Obtiene el período actual activo.
        Principio DRY: Método reutilizable.
        """
        try:
            current_date = get_mexico_now()

            current_period = session.exec(
                sqlmodel.select(Periods)
                .where(
                    (Periods.starts_on <= current_date) &
                    (Periods.ends_on >= current_date)
                )
            ).first()

            return current_period

        except Exception as e:
            print(f"❌ Error obteniendo período actual: {e}")
            return None


def run_monthly_closure():
    """
    Función wrapper para ejecutar el cierre mensual.
    Puede ser llamada por scheduler o manualmente.
    """
    return MonthlyClosureJob.execute_monthly_closure()


# Para testing manual
if __name__ == "__main__":
    print("🧪 Ejecutando cierre mensual manualmente...")
    success = run_monthly_closure()
    if success:
        print("✅ Cierre mensual exitoso")
    else:
        print("❌ Cierre mensual falló")
