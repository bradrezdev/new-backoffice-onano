"""
Servicio POO para procesamiento de pagos.
Orquesta el flujo completo: pago -> confirmación -> actualización PV -> comisiones.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import sqlmodel
from typing import Optional
from datetime import datetime, timezone

from database.orders import Orders, OrderStatus
from database.wallet import Wallets
from ..mlm_service.wallet_service import WalletService
from ..mlm_service.pv_update_service import PVUpdateService
from ..mlm_service.commission_service import CommissionService
from ..mlm_service.period_service import PeriodService


class PaymentService:
    """
    Servicio POO para procesamiento de pagos.
    Principio POO: Encapsula toda la lógica de pagos y confirmación.
    """

    @classmethod
    def process_wallet_payment(
        cls,
        session,
        order_id: int,
        member_id: int
    ) -> dict:
        """
        Procesa pago de orden con wallet virtual.

        Flujo completo:
        1. Validar orden y estado
        2. Validar balance de wallet
        3. Debitar monto de wallet
        4. Confirmar pago de orden (cambiar estado + timestamp)
        5. Actualizar PV del comprador y ancestros
        6. Disparar cálculo de comisiones

        Principio: Atomicidad - todo o nada.

        Args:
            session: Sesión de base de datos
            order_id: ID de la orden a pagar
            member_id: ID del usuario que paga

        Returns:
            Dict con:
            - success: bool
            - message: str
            - order_id: int (si exitoso)
        """
        try:
            # 1. Validar orden con ROW-LEVEL LOCK (evita double-payment)
            order = session.exec(
                sqlmodel.select(Orders)
                .where(Orders.id == order_id)
                .with_for_update()  # 🔒 Bloqueo pesimista
            ).first()

            if not order:
                return {
                    "success": False,
                    "message": f"Orden {order_id} no encontrada"
                }

            if order.member_id != member_id:
                return {
                    "success": False,
                    "message": "Orden no pertenece al usuario"
                }

            if order.status != OrderStatus.PENDING_PAYMENT.value:
                return {
                    "success": False,
                    "message": f"Orden no está en estado PENDING_PAYMENT (estado actual: {order.status})"
                }

            # Verificar idempotencia: orden ya procesada
            if order.payment_reference:
                print(f"⚠️  Orden {order_id} ya fue procesada (payment_reference: {order.payment_reference})")
                return {
                    "success": False,
                    "message": "Esta orden ya fue procesada anteriormente"
                }

            # Generar payment_reference único para idempotencia
            import uuid
            order.payment_reference = f"wallet_{uuid.uuid4().hex[:16]}"
            session.add(order)
            session.flush()

            # 2. Validar balance de wallet con ROW-LEVEL LOCK (evita race condition)
            wallet = session.exec(
                sqlmodel.select(Wallets)
                .where(Wallets.member_id == member_id)
                .with_for_update()  # 🔒 Bloqueo pesimista
            ).first()

            if not wallet:
                return {
                    "success": False,
                    "message": "No existe wallet para este usuario"
                }

            # Usar order.total (NO order.total_amount)
            if not wallet.has_sufficient_balance(order.total):
                return {
                    "success": False,
                    "message": f"Balance insuficiente: tiene {wallet.balance} {order.currency}, necesita {order.total} {order.currency}"
                }

            print(f"💳 Procesando pago con wallet para orden {order_id}...")

            # 3. Debitar monto de wallet (crea transacción automáticamente)
            payment_success = WalletService.pay_order_with_wallet(
                session=session,
                member_id=member_id,
                order_id=order_id,
                amount=order.total,
                currency=order.currency
            )

            if not payment_success:
                session.rollback()
                return {
                    "success": False,
                    "message": "Error al debitar wallet"
                }

            # 4. Confirmar pago de orden
            cls._confirm_order_payment(session, order)

            # 5. Actualizar PV del comprador y ancestros (CRÍTICO)
            pv_updated = PVUpdateService.process_order_pv_update(session, order_id)

            if not pv_updated:
                session.rollback()  # ⚠️ Revertir TODO (pago, confirmación, wallet)
                print(f"❌ Error crítico actualizando PV para orden {order_id}")
                return {
                    "success": False,
                    "message": "Error procesando puntos. Pago no completado. Intente nuevamente."
                }

            # 6. Disparar cálculo de comisiones
            try:
                cls._trigger_commissions(session, order)
            except Exception as e:
                session.rollback()  # ⚠️ Revertir TODO si falla comisiones
                print(f"❌ Error disparando comisiones: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "success": False,
                    "message": "Error procesando comisiones. Pago no completado."
                }

            # Commit final
            session.commit()

            print(f"✅ Pago procesado exitosamente para orden {order_id}")

            return {
                "success": True,
                "message": "Pago procesado exitosamente",
                "order_id": order_id
            }

        except Exception as e:
            session.rollback()
            print(f"❌ Error procesando pago con wallet para orden {order_id}: {e}")
            import traceback
            traceback.print_exc()

            return {
                "success": False,
                "message": f"Error interno: {str(e)}"
            }

    @classmethod
    def _confirm_order_payment(cls, session, order: Orders) -> None:
        """
        Confirma el pago de una orden.
        Cambia estado a PAYMENT_CONFIRMED y establece timestamp.

        Args:
            session: Sesión de base de datos
            order: Orden a confirmar
        """
        try:
            # Obtener período actual
            current_period = PeriodService.get_current_period(session)

            if not current_period:
                print(f"⚠️  No hay período actual, order.period_id será NULL")

            # Actualizar orden
            order.status = OrderStatus.PAYMENT_CONFIRMED.value
            order.payment_confirmed_at = datetime.now(timezone.utc)
            order.period_id = current_period.id if current_period else None
            order.payment_method = "wallet"

            session.add(order)
            session.flush()

            print(f"✅ Pago confirmado para orden {order.id} en período {order.period_id}")

        except Exception as e:
            print(f"❌ Error confirmando pago de orden {order.id}: {e}")
            raise

    @classmethod
    def _trigger_commissions(cls, session, order: Orders) -> None:
        """
        Dispara cálculo de comisiones para una orden confirmada.

        Comisiones disparadas INSTANTÁNEAMENTE:
        - Bono Directo (25% VN) - si total_vn > 0
        - Bono Rápido (30%/10%/5%) - solo si orden contiene kits
        - Bono Uninivel - para toda la línea ascendente según rango
        - Bono Matching - para embajadores en la línea ascendente

        ACTUALIZADO: Ahora calcula Uninivel y Matching en tiempo real.
        Esto permite que los usuarios vean sus ganancias proyectadas inmediatamente.

        Arquitectura: Adrian (Senior Dev) + Giovanni (QA Financial)

        Args:
            session: Sesión de base de datos
            order: Orden confirmada
        """
        try:
            print(f"\n💰 Disparando comisiones para orden {order.id}...")
            print(f"   👤 Comprador: member_id={order.member_id}")
            print(f"   💵 Total VN: ${order.total_vn:.2f}")
            print(f"   📦 Total PV: {order.total_pv}")
            print(f"   📅 Período: {order.period_id}")

            # 1. Bono Directo (25% del VN total)
            # Aplica tanto para kits como productos regulares
            if order.total_vn > 0:
                direct_commission_id = CommissionService.process_direct_bonus(
                    session=session,
                    buyer_id=order.member_id,
                    order_id=order.id,
                    vn_amount=order.total_vn
                )

                if direct_commission_id:
                    print(f"   ✅ Bono Directo generado (commission_id={direct_commission_id})")

            # 2. Bono Rápido (solo si la orden contiene kits)
            # Los kits pagan bono rápido instantáneo a 3 niveles
            commission_ids = CommissionService.process_fast_start_bonus(
                session=session,
                order_id=order.id
            )

            if commission_ids:
                print(f"   ✅ Bono Rápido generado para {len(commission_ids)} patrocinadores")

            # 3. Bono Uninivel - NUEVO: Se calcula INSTANTÁNEAMENTE
            # Se calcula para TODOS los ancestros del comprador según su rango
            # Esto permite que los usuarios vean sus ganancias proyectadas en tiempo real
            print(f"\n   🔄 Calculando Bono Uninivel para ancestros del comprador...")
            cls._trigger_unilevel_for_ancestors(session, order)

            # 4. Bono Matching - NUEVO: Se calcula INSTANTÁNEAMENTE
            # Solo para embajadores en la línea ascendente
            print(f"\n   🔄 Calculando Bono Matching para embajadores...")
            cls._trigger_matching_for_ambassadors(session, order)

            print(f"\n✅ TODAS las comisiones disparadas para orden {order.id}")

        except Exception as e:
            print(f"❌ Error disparando comisiones para orden {order.id}: {e}")
            # No lanzar excepción, comisiones se pueden recalcular
            import traceback
            traceback.print_exc()

    @classmethod
    def _trigger_unilevel_for_ancestors(cls, session, order: Orders) -> None:
        """
        Calcula el Bono Uninivel INCREMENTALMENTE para los ancestros del comprador.
        
        ARQUITECTURA OPTIMIZADA (Adrian + Elena + Giovanni):
        - Calcula comisiones SOLO para los ancestros directos del comprador
        - AGREGA comisiones nuevas (no borra las existentes)
        - Usa el VN de ESTA orden específica
        - Escalable: O(ancestros) en lugar de O(todos los usuarios)
        
        Flujo:
        1. Obtener ancestros del comprador con su profundidad
        2. Para cada ancestro:
           - Verificar su rango actual
           - Calcular % según rango y profundidad
           - Crear comisión Uninivel con VN de esta orden
        
        Arquitectura: Adrian (Senior Dev) + Elena (Backend) + Giovanni (QA Financial)
        
        Args:
            session: Sesión de base de datos
            order: Orden confirmada
        """
        try:
            from database.comissions import Commissions, BonusType, CommissionStatus
            from database.usertreepaths import UserTreePath
            from database.users import Users
            from database.ranks import Ranks
            from database.user_rank_history import UserRankHistory
            from ..mlm_service.exchange_service import ExchangeService
            
            # Porcentajes del Bono Uninivel por rango
            UNILEVEL_BONUS_PERCENTAGES = {
                "Visionario": [5, 8, 10],
                "Emprendedor": [5, 8, 10, 10],
                "Creativo": [5, 8, 10, 10, 5],
                "Innovador": [5, 8, 10, 10, 5, 4],
                "Embajador Transformador": [5, 8, 10, 10, 5, 4, 4, 3, 3, 0.5],
                "Embajador Inspirador": [5, 8, 10, 10, 5, 4, 4, 3, 3, 1.0],
                "Embajador Consciente": [5, 8, 10, 10, 5, 4, 4, 3, 3, 1.5],
                "Embajador Solidario": [5, 8, 10, 10, 5, 4, 4, 3, 3, 2.0]
            }
            
            if not order.period_id:
                print(f"   ⚠️  Orden {order.id} no tiene period_id asignado")
                return
            
            if not order.total_vn or order.total_vn <= 0:
                print(f"   ⚠️  Orden {order.id} no tiene VN")
                return

            # 1. Obtener todos los ancestros del comprador con su profundidad
            ancestor_paths = session.exec(
                sqlmodel.select(UserTreePath)
                .where(
                    (UserTreePath.descendant_id == order.member_id) &
                    (UserTreePath.depth > 0)
                )
                .order_by(UserTreePath.depth)
            ).all()

            print(f"   📊 Calculando Uninivel para {len(ancestor_paths)} ancestros del comprador...")
            
            commissions_created = 0

            for ancestor_path in ancestor_paths:
                ancestor_id = ancestor_path.ancestor_id
                depth = ancestor_path.depth
                
                # 2. Obtener rango actual del ancestro en este período
                rank_history = session.exec(
                    sqlmodel.select(UserRankHistory)
                    .where(
                        (UserRankHistory.member_id == ancestor_id) &
                        (UserRankHistory.period_id == order.period_id)
                    )
                    .order_by(sqlmodel.desc(UserRankHistory.rank_id))
                ).first()
                
                if not rank_history:
                    continue  # Usuario no tiene rango en este período
                
                # 3. Obtener información del rango
                rank = session.exec(
                    sqlmodel.select(Ranks).where(Ranks.id == rank_history.rank_id)
                ).first()
                
                if not rank:
                    continue
                
                # 4. Obtener porcentajes de Uninivel según rango
                percentages = UNILEVEL_BONUS_PERCENTAGES.get(rank.name, [])
                
                if not percentages:
                    continue  # Rango sin porcentajes (ej: "Sin rango")
                
                # 5. Verificar si este ancestro puede recibir comisión de este nivel
                if depth > len(percentages) and depth <= 9:
                    continue  # Fuera del alcance del rango
                
                # 6. Obtener porcentaje según profundidad
                if depth <= 9:
                    percentage = percentages[depth - 1]
                elif depth >= 10 and len(percentages) >= 10:
                    # Nivel 10+ para embajadores
                    percentage = percentages[9]
                else:
                    continue
                
                # 7. Calcular comisión para este ancestro
                commission_amount = order.total_vn * (percentage / 100)
                
                # 8. Obtener moneda del ancestro
                ancestor_user = session.exec(
                    sqlmodel.select(Users).where(Users.member_id == ancestor_id)
                ).first()
                
                if not ancestor_user:
                    continue
                
                ancestor_currency = ExchangeService.get_country_currency(
                    ancestor_user.country_cache or "MX"
                )
                
                # 9. Crear comisión Uninivel INCREMENTAL
                commission = Commissions(
                    member_id=ancestor_id,
                    bonus_type=BonusType.BONO_UNINIVEL.value,
                    source_member_id=order.member_id,
                    source_order_id=order.id,
                    period_id=order.period_id,
                    level_depth=depth if depth <= 10 else 10,
                    amount_vn=order.total_vn,
                    currency_origin=order.currency,
                    amount_converted=commission_amount,
                    currency_destination=ancestor_currency,
                    exchange_rate=1.0,
                    status=CommissionStatus.PENDING.value,
                    calculated_at=datetime.now(timezone.utc),
                    notes=f"Uninivel {percentage}% - Nivel {depth} - Orden {order.id} - VN: ${order.total_vn:.2f}"
                )
                
                session.add(commission)
                commissions_created += 1

            if commissions_created > 0:
                session.flush()
                print(f"   ✅ Uninivel: {commissions_created} comisiones creadas incrementalmente")
            else:
                print(f"   ℹ️  No se generaron comisiones Uninivel (ancestros sin rango elegible)")

        except Exception as e:
            print(f"   ❌ Error calculando Uninivel incremental: {e}")
            import traceback
            traceback.print_exc()
            # Hacer rollback para evitar transacciones inválidas
            try:
                session.rollback()
            except:
                pass

    @classmethod
    def _trigger_matching_for_ambassadors(cls, session, order: Orders) -> None:
        """
        Calcula el Bono Matching INCREMENTALMENTE para embajadores ancestros del comprador.
        
        ARQUITECTURA OPTIMIZADA (Adrian + Elena + Giovanni):
        - El Matching se calcula SOLO cuando se crea una comisión Uninivel
        - Solo se calcula para embajadores (rank_id >= 6) en la línea ascendente
        - Se aplica % del Matching sobre el Uninivel recién generado
        - Escalable: O(embajadores en línea) en lugar de O(todos los embajadores)
        
        Flujo:
        1. Buscar embajadores en la línea ascendente del comprador
        2. Para cada embajador:
           - Buscar comisiones Uninivel recién creadas de sus patrocinados directos
           - Aplicar % de Matching según su rango
           - Crear comisión Matching incremental
        
        Nota: El Matching se ejecuta DESPUÉS del Uninivel porque depende de él.
        
        Arquitectura: Adrian (Senior Dev) + Elena (Backend) + Giovanni (QA Financial)
        
        Args:
            session: Sesión de base de datos
            order: Orden confirmada
        """
        try:
            from database.comissions import Commissions, BonusType, CommissionStatus
            from database.usertreepaths import UserTreePath
            from database.users import Users
            from database.ranks import Ranks
            from database.user_rank_history import UserRankHistory
            from ..mlm_service.exchange_service import ExchangeService
            
            # Porcentajes del Bono Matching por rango
            MATCHING_BONUS_PERCENTAGES = {
                "Embajador Transformador": [30],
                "Embajador Inspirador": [30, 20],
                "Embajador Consciente": [30, 20, 10],
                "Embajador Solidario": [30, 20, 10, 5]
            }
            
            if not order.period_id:
                print(f"   ⚠️  Orden {order.id} no tiene period_id asignado")
                return

            # 1. Obtener ancestros del comprador que sean embajadores (rank_id >= 6)
            ancestor_paths = session.exec(
                sqlmodel.select(UserTreePath)
                .where(
                    (UserTreePath.descendant_id == order.member_id) &
                    (UserTreePath.depth > 0)
                )
            ).all()
            
            if not ancestor_paths:
                print(f"   ℹ️  Comprador no tiene ancestros (usuario raíz)")
                return

            print(f"   📊 Verificando {len(ancestor_paths)} ancestros para Matching...")
            
            commissions_created = 0

            for ancestor_path in ancestor_paths:
                ancestor_id = ancestor_path.ancestor_id
                
                # 2. Verificar si el ancestro es embajador (rank_id >= 6)
                rank_history = session.exec(
                    sqlmodel.select(UserRankHistory)
                    .where(
                        (UserRankHistory.member_id == ancestor_id) &
                        (UserRankHistory.period_id == order.period_id)
                    )
                    .order_by(sqlmodel.desc(UserRankHistory.rank_id))
                ).first()
                
                if not rank_history or rank_history.rank_id < 6:
                    continue  # No es embajador
                
                # 3. Obtener información del rango
                rank = session.exec(
                    sqlmodel.select(Ranks).where(Ranks.id == rank_history.rank_id)
                ).first()
                
                if not rank:
                    continue
                
                # 4. Obtener porcentajes de Matching según rango
                matching_percentages = MATCHING_BONUS_PERCENTAGES.get(rank.name, [])
                
                if not matching_percentages:
                    continue  # Rango sin Matching
                
                # 5. Obtener patrocinados DIRECTOS del embajador
                direct_sponsored = session.exec(
                    sqlmodel.select(UserTreePath.descendant_id)
                    .where(
                        (UserTreePath.ancestor_id == ancestor_id) &
                        (UserTreePath.depth == 1)
                    )
                ).all()
                
                if not direct_sponsored:
                    continue
                
                # 6. Para cada patrocinado directo, buscar sus comisiones Uninivel de ESTA orden
                for sponsored_id in direct_sponsored:
                    uninivel_commissions = session.exec(
                        sqlmodel.select(Commissions)
                        .where(
                            (Commissions.member_id == sponsored_id) &
                            (Commissions.source_order_id == order.id) &
                            (Commissions.bonus_type == BonusType.BONO_UNINIVEL.value) &
                            (Commissions.status == CommissionStatus.PENDING.value)
                        )
                    ).all()
                    
                    if not uninivel_commissions:
                        continue
                    
                    # 7. Calcular Matching: % del Uninivel del patrocinado directo
                    # Nivel 1 de Matching = 30% del Uninivel
                    matching_percentage = matching_percentages[0]  # Primer nivel de Matching
                    
                    for uninivel_comm in uninivel_commissions:
                        matching_amount = uninivel_comm.amount_converted * (matching_percentage / 100)
                        
                        # 8. Obtener moneda del embajador
                        ancestor_user = session.exec(
                            sqlmodel.select(Users).where(Users.member_id == ancestor_id)
                        ).first()
                        
                        if not ancestor_user:
                            continue
                        
                        ancestor_currency = ExchangeService.get_country_currency(
                            ancestor_user.country_cache or "MX"
                        )
                        
                        # 9. Crear comisión Matching INCREMENTAL
                        matching_commission = Commissions(
                            member_id=ancestor_id,
                            bonus_type=BonusType.BONO_MATCHING.value,
                            source_member_id=sponsored_id,
                            source_order_id=order.id,
                            period_id=order.period_id,
                            level_depth=1,  # Nivel 1 de Matching
                            amount_vn=uninivel_comm.amount_converted,
                            currency_origin=uninivel_comm.currency_destination,
                            amount_converted=matching_amount,
                            currency_destination=ancestor_currency,
                            exchange_rate=1.0,
                            status=CommissionStatus.PENDING.value,
                            calculated_at=datetime.now(timezone.utc),
                            notes=f"Matching {matching_percentage}% del Uninivel de {sponsored_id} - Orden {order.id}"
                        )
                        
                        session.add(matching_commission)
                        commissions_created += 1

            if commissions_created > 0:
                session.flush()
                print(f"   ✅ Matching: {commissions_created} comisiones creadas incrementalmente")
            else:
                print(f"   ℹ️  No se generaron comisiones Matching (no hay embajadores elegibles)")

        except Exception as e:
            print(f"   ❌ Error calculando Matching incremental: {e}")
            import traceback
            traceback.print_exc()
            # Hacer rollback para evitar transacciones inválidas
            try:
                session.rollback()
            except:
                pass

    @classmethod
    def validate_wallet_payment_available(
        cls,
        session,
        member_id: int,
        amount: float
    ) -> dict:
        """
        Valida si el usuario puede pagar con wallet.

        Args:
            session: Sesión de base de datos
            member_id: ID del usuario
            amount: Monto a validar

        Returns:
            Dict con:
            - available: bool
            - message: str
            - balance: float (si wallet existe)
            - currency: str (si wallet existe)
        """
        try:
            wallet = session.exec(
                sqlmodel.select(Wallets).where(Wallets.member_id == member_id)
            ).first()

            if not wallet:
                return {
                    "available": False,
                    "message": "No tienes una wallet creada",
                    "balance": 0.0
                }

            has_balance = wallet.has_sufficient_balance(amount)

            return {
                "available": has_balance,
                "message": "Balance suficiente" if has_balance else f"Balance insuficiente (tienes {wallet.balance} {wallet.currency})",
                "balance": wallet.balance,
                "currency": wallet.currency
            }

        except Exception as e:
            print(f"❌ Error validando wallet para usuario {member_id}: {e}")
            return {
                "available": False,
                "message": "Error al validar wallet",
                "balance": 0.0
            }
