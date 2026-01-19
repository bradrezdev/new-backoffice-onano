"""
Tests Unitarios - Bono Directo (Direct Bonus)

Objetivo: Validar el cálculo correcto del Bono Directo (25% del VN).

Reglas de Negocio:
- 25% del VN total de la orden
- Solo al patrocinador directo (sponsor_id)
- Aplica tanto para kits como productos regulares
- Conversión a moneda del patrocinador

Autor: QA Engineer Giovann
Fecha: Octubre 2025
"""

import pytest
from datetime import datetime, timezone
from sqlmodel import select

from database.comissions import Commissions, BonusType
from NNProtect_new_website.modules.network.backend.commission_service import CommissionService


@pytest.mark.critical
@pytest.mark.direct_bonus
class TestDirectBonus:
    """
    Suite de tests para el Bono Directo (25% del VN).
    """

    def test_direct_bonus_25_percent_of_vn(
        self,
        db_session,
        test_network_simple,
        test_product_dna_60,
        create_test_order
    ):
        """
        Test: Bono Directo calcula 25% del VN correctamente

        Escenario:
            A → B → C

        Acción:
            B compra producto DNA 60 (VN=1,465 MXN)

        Esperado:
            - A recibe 25% de 1,465 = 366.25 MXN ✅
        """
        # Arrange
        users = test_network_simple
        buyer = users['B']
        sponsor = users['A']

        # Act: B compra producto
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_product_dna_60, 1)],
            payment_confirmed=True
        )

        vn_amount = 1465  # VN del producto

        # Act: Procesar Bono Directo
        commission_id = CommissionService.process_direct_bonus(
            session=db_session,
            buyer_id=buyer.member_id,
            order_id=order.id,
            vn_amount=vn_amount
        )

        # Assert: Comisión creada
        assert commission_id is not None, "Debe crearse comisión de Bono Directo"

        # Assert: A recibe 25% del VN
        commission = db_session.get(Commissions, commission_id)
        assert commission is not None
        assert commission.member_id == sponsor.member_id
        assert commission.bonus_type == BonusType.BONO_DIRECTO.value
        assert commission.level_depth == 1, "Bono Directo siempre es nivel 1"

        expected_amount = vn_amount * 0.25
        assert abs(commission.amount_vn - expected_amount) < 0.01, \
            f"Esperado {expected_amount}, Obtenido {commission.amount_vn}"

    def test_direct_bonus_on_kit_purchase(
        self,
        db_session,
        test_network_simple,
        test_kit_full_protect,
        create_test_order
    ):
        """
        Test: Bono Directo NO se aplica en kits (VN=0)

        Escenario:
            A → B → C

        Acción:
            B compra kit Full Protect (VN=0)

        Esperado:
            - ⚠️ Como kits tienen VN=0, NO se genera comisión
            - O se genera comisión de 0 (depende de implementación)
        """
        # Arrange
        users = test_network_simple
        buyer = users['B']

        # Act: B compra kit
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_kit_full_protect, 1)],
            payment_confirmed=True
        )

        vn_amount = 0  # ⚠️ Kits NO generan VN

        # Act: Procesar Bono Directo
        commission_id = CommissionService.process_direct_bonus(
            session=db_session,
            buyer_id=buyer.member_id,
            order_id=order.id,
            vn_amount=vn_amount
        )

        # Assert: Si VN=0, puede retornar None o crear comisión de 0
        # Aquí validamos que NO se cree comisión si VN=0
        if commission_id is None:
            # Implementación correcta: No crear comisión si VN=0
            assert True, "Correcto: No se crea comisión si VN=0"
        else:
            # O se crea con amount=0
            commission = db_session.get(Commissions, commission_id)
            assert commission.amount_vn == 0, "Si se crea, amount_vn debe ser 0"

    def test_direct_bonus_on_product_purchase(
        self,
        db_session,
        test_network_simple,
        test_product_dna_60,
        create_test_order
    ):
        """
        Test: Bono Directo aplica correctamente en productos regulares

        Escenario:
            A → B → C

        Acción:
            C compra 2x DNA 60 (2 * VN=1,465 = 2,930 VN total)

        Esperado:
            - B recibe 25% de 2,930 = 732.5 MXN ✅
        """
        # Arrange
        users = test_network_simple
        buyer = users['C']
        sponsor = users['B']

        # Act: C compra 2 productos
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_product_dna_60, 2)],  # Quantity = 2
            payment_confirmed=True
        )

        vn_amount = 1465 * 2  # VN total

        # Act: Procesar Bono Directo
        commission_id = CommissionService.process_direct_bonus(
            session=db_session,
            buyer_id=buyer.member_id,
            order_id=order.id,
            vn_amount=vn_amount
        )

        # Assert: B recibe 25% de 2,930
        commission = db_session.get(Commissions, commission_id)
        assert commission is not None
        assert commission.member_id == sponsor.member_id

        expected_amount = vn_amount * 0.25
        assert abs(commission.amount_vn - expected_amount) < 0.01, \
            f"Esperado {expected_amount}, Obtenido {commission.amount_vn}"

    @pytest.mark.edge_case
    def test_direct_bonus_no_sponsor(
        self,
        db_session,
        create_test_user,
        test_product_dna_60,
        create_test_order
    ):
        """
        Test: Bono Directo cuando usuario no tiene sponsor

        Escenario:
            Usuario A (sin sponsor)

        Acción:
            A compra producto

        Esperado:
            - NO se crea comisión ✅
            - Retorna None ✅
        """
        # Arrange: Usuario sin sponsor
        user_a = create_test_user(member_id=1000, sponsor_id=None)

        # Act: A compra producto
        order = create_test_order(
            member_id=user_a.member_id,
            items=[(test_product_dna_60, 1)],
            payment_confirmed=True
        )

        vn_amount = 1465

        # Act: Procesar Bono Directo
        commission_id = CommissionService.process_direct_bonus(
            session=db_session,
            buyer_id=user_a.member_id,
            order_id=order.id,
            vn_amount=vn_amount
        )

        # Assert: No se crea comisión
        assert commission_id is None, "No debe crearse comisión si no hay sponsor"

    def test_direct_bonus_currency_conversion(
        self,
        db_session,
        test_network_multi_country,
        test_product_dna_60,
        create_test_order,
        setup_exchange_rates
    ):
        """
        Test: Bono Directo con conversión de moneda

        Escenario:
            A(Mexico, MXN) → B(USA, USD)

        Acción:
            B compra producto en USD (VN=1,465 USD)

        Esperado:
            - A recibe 25% en MXN (convertido de USD) ✅
            - Exchange rate guardado en comisión ✅
        """
        # Arrange
        users = test_network_multi_country
        buyer = users['B']  # USA
        sponsor = users['A']  # Mexico

        # Act: B compra producto en USA
        order = create_test_order(
            member_id=buyer.member_id,
            items=[(test_product_dna_60, 1)],
            country="USA",
            payment_confirmed=True
        )

        vn_amount = 1465  # VN del producto (mismo en todos los países)

        # Act: Procesar Bono Directo
        commission_id = CommissionService.process_direct_bonus(
            session=db_session,
            buyer_id=buyer.member_id,
            order_id=order.id,
            vn_amount=vn_amount
        )

        # Assert: Comisión creada
        commission = db_session.get(Commissions, commission_id)
        assert commission is not None
        assert commission.member_id == sponsor.member_id

        # Assert: Conversión de moneda
        assert commission.currency_origin == "USD", "Origen debe ser USD"
        assert commission.currency_destination == "MXN", "Destino debe ser MXN"
        assert commission.amount_vn == vn_amount * 0.25, "amount_vn en USD"
        assert commission.amount_converted > 0, "amount_converted debe ser > 0 en MXN"

    def test_direct_bonus_multiple_orders(
        self,
        db_session,
        test_network_simple,
        test_product_dna_60,
        create_test_order
    ):
        """
        Test: Bono Directo en múltiples órdenes independientes

        Escenario:
            A → B

        Acción:
            B compra producto (orden 1)
            B compra producto (orden 2)

        Esperado:
            - A recibe 2 comisiones independientes ✅
            - Total: 2 * (25% de 1,465) = 732.5 MXN ✅
        """
        # Arrange
        users = test_network_simple
        buyer = users['B']
        sponsor = users['A']

        # Act: Primera orden
        order_1 = create_test_order(
            member_id=buyer.member_id,
            items=[(test_product_dna_60, 1)],
            payment_confirmed=True
        )

        commission_id_1 = CommissionService.process_direct_bonus(
            session=db_session,
            buyer_id=buyer.member_id,
            order_id=order_1.id,
            vn_amount=1465
        )

        # Act: Segunda orden
        order_2 = create_test_order(
            member_id=buyer.member_id,
            items=[(test_product_dna_60, 1)],
            payment_confirmed=True
        )

        commission_id_2 = CommissionService.process_direct_bonus(
            session=db_session,
            buyer_id=buyer.member_id,
            order_id=order_2.id,
            vn_amount=1465
        )

        # Assert: 2 comisiones creadas
        assert commission_id_1 is not None
        assert commission_id_2 is not None
        assert commission_id_1 != commission_id_2, "Deben ser comisiones diferentes"

        # Assert: Ambas comisiones para A
        commissions = db_session.exec(
            select(Commissions).where(
                (Commissions.member_id == sponsor.member_id) &
                (Commissions.bonus_type == BonusType.BONO_DIRECTO.value)
            )
        ).all()

        assert len(commissions) == 2, "Deben haber 2 comisiones"

        # Assert: Suma total correcta
        total_commissions = sum(c.amount_vn for c in commissions)
        expected_total = 2 * (1465 * 0.25)
        assert abs(total_commissions - expected_total) < 0.01, \
            f"Total esperado {expected_total}, Obtenido {total_commissions}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
