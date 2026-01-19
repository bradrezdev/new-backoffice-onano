"""
Tests Unitarios - Bono Rápido (Fast Start Bonus)

Objetivo: Validar el cálculo correcto del Bono Rápido en todos los escenarios.

Reglas de Negocio:
- Solo aplica para productos tipo 'kit' (presentation="kit")
- Paga 30%/10%/5% del PV del kit a niveles 1/2/3
- Instantáneo al confirmar pago
- Conversión a moneda del patrocinador
- Si no hay 3 niveles completos, solo paga los disponibles

Autor: QA Engineer Giovann
Fecha: Octubre 2025
"""

import pytest
from datetime import datetime, timezone
from sqlmodel import select

from database.comissions import Commissions, BonusType
from NNProtect_new_website.modules.network.backend.commission_service import CommissionService


@pytest.mark.critical
@pytest.mark.fast_bonus
class TestFastStartBonus:
    """
    Suite de tests para el Bono Rápido (Fast Start Bonus).
    """

    def test_fast_bonus_with_3_levels_complete(
        self,
        db_session,
        test_network_4_levels,
        test_kit_full_protect,
        create_test_order
    ):
        """
        Test: Bono Rápido con 3 niveles completos

        Escenario:
            A → B → C → D (4 niveles)

        Acción:
            D compra kit Full Protect (PV=2,930)

        Esperado:
            - C recibe 30% (879 PV) ✅
            - B recibe 10% (293 PV) ✅
            - A recibe 5% (146.5 PV) ✅
            - Total 3 comisiones creadas ✅
        """
        # Arrange
        users = test_network_4_levels
        buyer = users['D']

        # Act: D compra kit
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_kit_full_protect, 1)],
            payment_confirmed=True
        )

        # Act: Procesar Bono Rápido
        commission_ids = CommissionService.process_fast_start_bonus(db_session, order.id)

        # Assert: Se crearon 3 comisiones
        assert len(commission_ids) == 3, "Deben crearse 3 comisiones (niveles 1, 2, 3)"

        # Assert: C recibe 30% (nivel 1)
        commission_c = db_session.exec(
            select(Commissions).where(
                (Commissions.member_id == users['C'].member_id) &
                (Commissions.bonus_type == BonusType.BONO_RAPIDO.value)
            )
        ).first()
        assert commission_c is not None, "C debe recibir comisión"
        assert commission_c.level_depth == 1
        expected_amount_c = 2930 * 0.30
        assert abs(commission_c.amount_vn - expected_amount_c) < 0.01, \
            f"C debe recibir 30% de 2930 = {expected_amount_c}, obtuvo {commission_c.amount_vn}"

        # Assert: B recibe 10% (nivel 2)
        commission_b = db_session.exec(
            select(Commissions).where(
                (Commissions.member_id == users['B'].member_id) &
                (Commissions.bonus_type == BonusType.BONO_RAPIDO.value)
            )
        ).first()
        assert commission_b is not None, "B debe recibir comisión"
        assert commission_b.level_depth == 2
        expected_amount_b = 2930 * 0.10
        assert abs(commission_b.amount_vn - expected_amount_b) < 0.01, \
            f"B debe recibir 10% de 2930 = {expected_amount_b}, obtuvo {commission_b.amount_vn}"

        # Assert: A recibe 5% (nivel 3)
        commission_a = db_session.exec(
            select(Commissions).where(
                (Commissions.member_id == users['A'].member_id) &
                (Commissions.bonus_type == BonusType.BONO_RAPIDO.value)
            )
        ).first()
        assert commission_a is not None, "A debe recibir comisión"
        assert commission_a.level_depth == 3
        expected_amount_a = 2930 * 0.05
        assert abs(commission_a.amount_vn - expected_amount_a) < 0.01, \
            f"A debe recibir 5% de 2930 = {expected_amount_a}, obtuvo {commission_a.amount_vn}"

    @pytest.mark.edge_case
    def test_fast_bonus_with_only_2_levels(
        self,
        db_session,
        test_network_simple,
        test_kit_full_protect,
        create_test_order
    ):
        """
        Test: Bono Rápido con solo 2 niveles disponibles

        Escenario:
            A → B → C (3 niveles, pero C no tiene upline nivel 3)

        Acción:
            C compra kit Full Protect (PV=2,930)

        Esperado:
            - B recibe 30% (nivel 1) ✅
            - A recibe 10% (nivel 2) ✅
            - Nivel 3 NO existe, no se paga ✅
            - Total 2 comisiones creadas ✅
        """
        # Arrange
        users = test_network_simple
        buyer = users['C']

        # Act: C compra kit
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_kit_full_protect, 1)],
            payment_confirmed=True
        )

        # Act: Procesar Bono Rápido
        commission_ids = CommissionService.process_fast_start_bonus(db_session, order.id)

        # Assert: Solo 2 comisiones
        assert len(commission_ids) == 2, "Deben crearse solo 2 comisiones (niveles 1 y 2 disponibles)"

        # Assert: B recibe 30%
        commission_b = db_session.exec(
            select(Commissions).where(
                (Commissions.member_id == users['B'].member_id) &
                (Commissions.bonus_type == BonusType.BONO_RAPIDO.value)
            )
        ).first()
        assert commission_b is not None
        assert commission_b.level_depth == 1
        assert abs(commission_b.amount_vn - 2930 * 0.30) < 0.01

        # Assert: A recibe 10%
        commission_a = db_session.exec(
            select(Commissions).where(
                (Commissions.member_id == users['A'].member_id) &
                (Commissions.bonus_type == BonusType.BONO_RAPIDO.value)
            )
        ).first()
        assert commission_a is not None
        assert commission_a.level_depth == 2
        assert abs(commission_a.amount_vn - 2930 * 0.10) < 0.01

    @pytest.mark.edge_case
    def test_fast_bonus_with_no_sponsor(
        self,
        db_session,
        create_test_user,
        test_kit_full_protect,
        create_test_order
    ):
        """
        Test: Bono Rápido cuando usuario no tiene sponsor

        Escenario:
            Usuario A (sin sponsor)

        Acción:
            A compra kit Full Protect

        Esperado:
            - NO se crean comisiones ✅
            - commission_ids = [] ✅
        """
        # Arrange: Usuario sin sponsor
        user_a = create_test_user(member_id=1000, sponsor_id=None)

        # Act: A compra kit
        order = create_test_order(
            member_id=user_a.member_id,
            items=[(test_kit_full_protect, 1)],
            payment_confirmed=True
        )

        # Act: Procesar Bono Rápido
        commission_ids = CommissionService.process_fast_start_bonus(db_session, order.id)

        # Assert: No se crean comisiones
        assert len(commission_ids) == 0, "No deben crearse comisiones si no hay sponsor"

    def test_fast_bonus_multiple_kits_same_order(
        self,
        db_session,
        test_network_4_levels,
        test_kit_full_protect,
        create_test_order
    ):
        """
        Test: Bono Rápido con múltiples kits en la misma orden

        Escenario:
            A → B → C → D

        Acción:
            D compra 2x kit Full Protect (2 * PV=2,930 = 5,860 PV total)

        Esperado:
            - C recibe 30% de 5,860 = 1,758 PV ✅
            - B recibe 10% de 5,860 = 586 PV ✅
            - A recibe 5% de 5,860 = 293 PV ✅
        """
        # Arrange
        users = test_network_4_levels
        buyer = users['D']

        # Act: D compra 2 kits
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_kit_full_protect, 2)],  # Quantity = 2
            payment_confirmed=True
        )

        # Act: Procesar Bono Rápido
        commission_ids = CommissionService.process_fast_start_bonus(db_session, order.id)

        # Assert: 3 comisiones
        assert len(commission_ids) == 3

        # Assert: C recibe 30% de 5,860
        commission_c = db_session.exec(
            select(Commissions).where(
                (Commissions.member_id == users['C'].member_id) &
                (Commissions.bonus_type == BonusType.BONO_RAPIDO.value)
            )
        ).first()
        assert commission_c is not None
        total_pv = 2930 * 2
        expected_c = total_pv * 0.30
        assert abs(commission_c.amount_vn - expected_c) < 0.01, \
            f"C debe recibir 30% de {total_pv} = {expected_c}"

    def test_fast_bonus_currency_conversion_mx_to_usa(
        self,
        db_session,
        test_network_multi_country,
        test_kit_full_protect,
        create_test_order,
        setup_exchange_rates
    ):
        """
        Test: Bono Rápido con conversión de moneda MXN → USD

        Escenario:
            A(Mexico, MXN) → B(USA, USD) → C(Colombia, COP)

        Acción:
            C compra kit en COP (PV=2,930)

        Esperado:
            - B recibe comisión en USD (convertido de COP) ✅
            - A recibe comisión en MXN (convertido de COP) ✅
            - Exchange rates guardados en comisión ✅
        """
        # Arrange
        users = test_network_multi_country
        buyer = users['C']  # Colombia

        # Act: C compra kit
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_kit_full_protect, 1)],
            country="Colombia",
            payment_confirmed=True
        )

        # Act: Procesar Bono Rápido
        commission_ids = CommissionService.process_fast_start_bonus(db_session, order.id)

        # Assert: 2 comisiones (B y A)
        assert len(commission_ids) == 2

        # Assert: B recibe en USD
        commission_b = db_session.exec(
            select(Commissions).where(
                (Commissions.member_id == users['B'].member_id) &
                (Commissions.bonus_type == BonusType.BONO_RAPIDO.value)
            )
        ).first()
        assert commission_b is not None
        assert commission_b.currency_destination == "USD", "B debe recibir en USD"
        assert commission_b.currency_origin == "COP", "Origen es COP"

        # Assert: A recibe en MXN
        commission_a = db_session.exec(
            select(Commissions).where(
                (Commissions.member_id == users['A'].member_id) &
                (Commissions.bonus_type == BonusType.BONO_RAPIDO.value)
            )
        ).first()
        assert commission_a is not None
        assert commission_a.currency_destination == "MXN", "A debe recibir en MXN"
        assert commission_a.currency_origin == "COP", "Origen es COP"

    @pytest.mark.critical
    def test_fast_bonus_not_triggered_by_products(
        self,
        db_session,
        test_network_simple,
        test_product_dna_60,
        create_test_order
    ):
        """
        Test: Bono Rápido NO se activa con productos regulares

        Escenario:
            A → B → C

        Acción:
            C compra DNA 60 Cápsulas (NO es kit)

        Esperado:
            - NO se crean comisiones de Bono Rápido ✅
            - Los productos regulares NO activan Bono Rápido ✅
        """
        # Arrange
        users = test_network_simple
        buyer = users['C']

        # Act: C compra producto regular (NO kit)
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_product_dna_60, 1)],
            payment_confirmed=True
        )

        # Act: Procesar Bono Rápido
        commission_ids = CommissionService.process_fast_start_bonus(db_session, order.id)

        # Assert: NO se crean comisiones
        assert len(commission_ids) == 0, "Los productos regulares NO deben activar Bono Rápido"

        # Assert: No hay comisiones en BD
        commissions = db_session.exec(
            select(Commissions).where(
                Commissions.bonus_type == BonusType.BONO_RAPIDO.value
            )
        ).all()
        assert len(commissions) == 0, "No debe haber comisiones de Bono Rápido"

    def test_fast_bonus_percentages_accuracy(
        self,
        db_session,
        test_network_4_levels,
        test_kit_full_protect,
        create_test_order
    ):
        """
        Test: Validar precisión de porcentajes del Bono Rápido

        Objetivo:
            Verificar que los cálculos sean exactos con 2 decimales.
        """
        # Arrange
        users = test_network_4_levels
        buyer = users['D']

        # Act: D compra kit
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_kit_full_protect, 1)],
            payment_confirmed=True
        )

        # Act: Procesar Bono Rápido
        CommissionService.process_fast_start_bonus(db_session, order.id)

        # Assert: Validar porcentajes exactos
        expected_percentages = {
            users['C'].member_id: 0.30,  # Nivel 1: 30%
            users['B'].member_id: 0.10,  # Nivel 2: 10%
            users['A'].member_id: 0.05,  # Nivel 3: 5%
        }

        kit_pv = 2930

        for member_id, expected_percentage in expected_percentages.items():
            commission = db_session.exec(
                select(Commissions).where(
                    (Commissions.member_id == member_id) &
                    (Commissions.bonus_type == BonusType.BONO_RAPIDO.value)
                )
            ).first()

            assert commission is not None, f"Comisión para member_id={member_id} no encontrada"

            expected_amount = kit_pv * expected_percentage
            actual_amount = commission.amount_vn

            # Validar con precisión de 2 decimales
            assert abs(actual_amount - expected_amount) < 0.01, \
                f"member_id={member_id}: Esperado {expected_amount:.2f}, Obtenido {actual_amount:.2f}"

    def test_fast_bonus_order_not_confirmed(
        self,
        db_session,
        test_network_simple,
        test_kit_full_protect,
        create_test_order
    ):
        """
        Test: Bono Rápido NO se activa si orden no está confirmada

        Escenario:
            A → B → C

        Acción:
            C crea orden de kit pero NO confirma pago (status=DRAFT)

        Esperado:
            - NO se crean comisiones ✅
        """
        # Arrange
        users = test_network_simple
        buyer = users['C']

        # Act: C crea orden pero NO confirma pago
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_kit_full_protect, 1)],
            payment_confirmed=False  # ⚠️ CRÍTICO: No confirmada
        )

        # Act: Intentar procesar Bono Rápido
        commission_ids = CommissionService.process_fast_start_bonus(db_session, order.id)

        # Assert: NO se crean comisiones
        assert len(commission_ids) == 0, "No deben crearse comisiones si pago no está confirmado"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
