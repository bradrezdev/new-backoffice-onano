"""
Servicio de tareas programadas para MLM.
Maneja jobs automáticos: períodos, reseteo PV/PVG, etc.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import reflex as rx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone

from .period_service import PeriodService
from .pv_reset_service import PVResetService


class SchedulerService:
    """
    Servicio POO para manejo de tareas programadas.
    Principio POO: Encapsula toda la lógica de scheduling.
    """

    _scheduler: BackgroundScheduler = None
    _started: bool = False

    @classmethod
    def start_scheduler(cls):
        """
        Inicia el scheduler con todas las tareas programadas.
        Principio KISS: Configuración simple y directa.
        """
        if cls._started:
            print("⚠️  Scheduler ya está corriendo")
            return

        try:
            cls._scheduler = BackgroundScheduler(timezone='UTC')

            # Tarea: Crear nuevo periodo y resetear PV/PVG el día 1 a las 00:00:00 UTC
            cls._scheduler.add_job(
                func=cls._monthly_period_and_reset_job,
                trigger=CronTrigger(day=1, hour=0, minute=0, second=0),
                id='monthly_period_and_reset',
                name='Creación de periodo y reseteo mensual PV/PVG',
                replace_existing=True
            )

            # Tarea: Finalizar periodos vencidos diariamente a las 00:01 UTC
            cls._scheduler.add_job(
                func=cls._finalize_periods_job,
                trigger=CronTrigger(hour=0, minute=1, second=0),
                id='finalize_periods',
                name='Finalización de períodos vencidos',
                replace_existing=True
            )

            cls._scheduler.start()
            cls._started = True
            print("✅ Scheduler iniciado correctamente")

        except Exception as e:
            print(f"❌ Error iniciando scheduler: {e}")

    @classmethod
    def stop_scheduler(cls):
        """
        Detiene el scheduler.
        """
        if cls._scheduler and cls._started:
            cls._scheduler.shutdown()
            cls._started = False
            print("✅ Scheduler detenido")

    @classmethod
    def _monthly_period_and_reset_job(cls):
        """
        Job que se ejecuta el día 1 de cada mes a las 00:00:00 UTC.
        1. Resetea PV/PVG de todos los usuarios a 0
        2. Crea nuevo periodo para el mes
        3. Ajusta rangos según valores reseteados
        """
        try:
            print(f"[{datetime.now(timezone.utc)}] 🔄 Iniciando proceso mensual: reseteo y nuevo periodo...")

            with rx.session() as session:
                # Paso 1: Resetear PV/PVG
                print("📊 Paso 1/3: Reseteando PV/PVG...")
                PVResetService.monthly_reset_and_rank_adjustment(session)

                # Paso 2: Crear nuevo periodo
                print("📅 Paso 2/3: Creando nuevo periodo...")
                PeriodService.auto_create_current_month_period(session)

                # Paso 3: Commit de cambios
                session.commit()
                print("✅ Proceso mensual completado exitosamente")

        except Exception as e:
            print(f"❌ Error en proceso mensual: {e}")
            import traceback
            traceback.print_exc()

    @classmethod
    def _finalize_periods_job(cls):
        """
        Job para finalizar periodos vencidos.
        Se ejecuta diariamente a las 00:01 UTC.
        """
        try:
            print(f"[{datetime.now(timezone.utc)}] 🔍 Verificando periodos vencidos...")

            with rx.session() as session:
                finalized_count = PeriodService.auto_finalize_past_periods(session)
                session.commit()

                if finalized_count > 0:
                    print(f"✅ {finalized_count} periodo(s) finalizado(s)")
                else:
                    print("ℹ️  No hay periodos por finalizar")

        except Exception as e:
            print(f"❌ Error finalizando periodos: {e}")

    @classmethod
    def run_job_manually(cls, job_id: str):
        """
        Ejecuta un job manualmente (útil para testing).

        Args:
            job_id: 'monthly_period_and_reset' o 'finalize_periods'
        """
        if job_id == 'monthly_period_and_reset':
            cls._monthly_period_and_reset_job()
        elif job_id == 'finalize_periods':
            cls._finalize_periods_job()
        else:
            print(f"⚠️  Job ID '{job_id}' no reconocido")
