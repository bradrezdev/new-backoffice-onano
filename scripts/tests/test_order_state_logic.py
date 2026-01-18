#!/usr/bin/env python3
"""
Script de testing para verificar la lógica de OrderState sin necesidad de Reflex
"""

from datetime import datetime
from typing import List, Dict


class OrderStateLogicTester:
    """Simula la lógica del OrderState para testing"""

    def __init__(self):
        self.all_orders = []
        self.search_query = ""
        self.status_filter = "Todas"
        self.sort_by = "Más reciente"
        self.current_page = 1
        self.items_per_page = 10

    def _parse_date_for_sorting(self, date_str: str) -> datetime:
        """Convierte fecha DD/MM/YYYY a datetime"""
        try:
            if not date_str:
                return datetime.min
            return datetime.strptime(date_str, "%d/%m/%Y")
        except Exception:
            return datetime.min

    def _parse_amount_for_sorting(self, amount_str: str) -> float:
        """Convierte "$1,746.50" a float"""
        try:
            if not amount_str:
                return 0.0
            clean_amount = amount_str.replace('$', '').replace(',', '').strip()
            return float(clean_amount)
        except Exception:
            return 0.0

    def get_filtered_orders(self) -> List[Dict]:
        """Lógica de filtrado (copia de filtered_orders computed var)"""
        if not self.all_orders:
            return []

        orders = self.all_orders.copy()

        # 1. Filtrar por búsqueda
        if self.search_query.strip():
            query_lower = self.search_query.lower().strip()
            orders = [
                order for order in orders
                if query_lower in str(order.get('order_number', '')).lower()
            ]

        # 2. Filtrar por estado
        if self.status_filter != "Todas":
            orders = [
                order for order in orders
                if order.get('status', '').lower() == self.status_filter.lower()
            ]

        # 3. Ordenar
        if self.sort_by == "Más reciente":
            orders.sort(
                key=lambda x: self._parse_date_for_sorting(x.get('purchase_date', '')),
                reverse=True
            )
        elif self.sort_by == "Más antiguo":
            orders.sort(
                key=lambda x: self._parse_date_for_sorting(x.get('purchase_date', '')),
                reverse=False
            )
        elif self.sort_by == "Mayor monto":
            orders.sort(
                key=lambda x: self._parse_amount_for_sorting(x.get('total', '$0')),
                reverse=True
            )
        elif self.sort_by == "Menor monto":
            orders.sort(
                key=lambda x: self._parse_amount_for_sorting(x.get('total', '$0')),
                reverse=False
            )

        # 4. Paginación
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page

        return orders[start_idx:end_idx]

    def get_total_orders(self) -> int:
        """Total de órdenes después de filtros"""
        if not self.all_orders:
            return 0

        orders = self.all_orders.copy()

        if self.search_query.strip():
            query_lower = self.search_query.lower().strip()
            orders = [
                order for order in orders
                if query_lower in str(order.get('order_number', '')).lower()
            ]

        if self.status_filter != "Todas":
            orders = [
                order for order in orders
                if order.get('status', '').lower() == self.status_filter.lower()
            ]

        return len(orders)


def test_filtering():
    """Test de filtrado"""
    print("\n🧪 TEST 1: Filtrado por estado")
    print("=" * 60)

    tester = OrderStateLogicTester()

    # Datos de prueba
    tester.all_orders = [
        {'order_number': '1', 'status': 'Entregado', 'total': '$100', 'purchase_date': '01/01/2025'},
        {'order_number': '2', 'status': 'Pendiente', 'total': '$200', 'purchase_date': '02/01/2025'},
        {'order_number': '3', 'status': 'Entregado', 'total': '$300', 'purchase_date': '03/01/2025'},
        {'order_number': '4', 'status': 'Cancelado', 'total': '$400', 'purchase_date': '04/01/2025'},
    ]

    # Test: Filtrar solo "Entregado"
    tester.status_filter = "Entregado"
    filtered = tester.get_filtered_orders()

    assert len(filtered) == 2, f"❌ Esperaba 2 órdenes, obtuvo {len(filtered)}"
    assert all(o['status'] == 'Entregado' for o in filtered), "❌ No todas las órdenes son 'Entregado'"

    print(f"✅ Filtro por estado funciona correctamente")
    print(f"   - Total órdenes: {len(tester.all_orders)}")
    print(f"   - Filtrado 'Entregado': {len(filtered)}")


def test_search():
    """Test de búsqueda"""
    print("\n🧪 TEST 2: Búsqueda por número de orden")
    print("=" * 60)

    tester = OrderStateLogicTester()

    tester.all_orders = [
        {'order_number': '12345', 'status': 'Entregado', 'total': '$100', 'purchase_date': '01/01/2025'},
        {'order_number': '67890', 'status': 'Pendiente', 'total': '$200', 'purchase_date': '02/01/2025'},
        {'order_number': '11111', 'status': 'Entregado', 'total': '$300', 'purchase_date': '03/01/2025'},
    ]

    # Test: Buscar "123"
    tester.search_query = "123"
    filtered = tester.get_filtered_orders()

    assert len(filtered) == 1, f"❌ Esperaba 1 orden, obtuvo {len(filtered)}"
    assert filtered[0]['order_number'] == '12345', "❌ Orden incorrecta"

    print(f"✅ Búsqueda funciona correctamente")
    print(f"   - Query: '{tester.search_query}'")
    print(f"   - Resultados: {len(filtered)}")


def test_sorting():
    """Test de ordenamiento"""
    print("\n🧪 TEST 3: Ordenamiento")
    print("=" * 60)

    tester = OrderStateLogicTester()

    tester.all_orders = [
        {'order_number': '1', 'status': 'Entregado', 'total': '$500', 'purchase_date': '15/05/2025'},
        {'order_number': '2', 'status': 'Entregado', 'total': '$100', 'purchase_date': '10/01/2025'},
        {'order_number': '3', 'status': 'Entregado', 'total': '$300', 'purchase_date': '20/10/2025'},
    ]

    # Test 1: Más reciente
    tester.sort_by = "Más reciente"
    filtered = tester.get_filtered_orders()
    assert filtered[0]['order_number'] == '3', "❌ Orden más reciente incorrecta"
    print(f"✅ Ordenamiento 'Más reciente': Correcto")

    # Test 2: Más antiguo
    tester.sort_by = "Más antiguo"
    filtered = tester.get_filtered_orders()
    assert filtered[0]['order_number'] == '2', "❌ Orden más antigua incorrecta"
    print(f"✅ Ordenamiento 'Más antiguo': Correcto")

    # Test 3: Mayor monto
    tester.sort_by = "Mayor monto"
    filtered = tester.get_filtered_orders()
    assert filtered[0]['order_number'] == '1', "❌ Mayor monto incorrecto"
    print(f"✅ Ordenamiento 'Mayor monto': Correcto")

    # Test 4: Menor monto
    tester.sort_by = "Menor monto"
    filtered = tester.get_filtered_orders()
    assert filtered[0]['order_number'] == '2', "❌ Menor monto incorrecto"
    print(f"✅ Ordenamiento 'Menor monto': Correcto")


def test_pagination():
    """Test de paginación"""
    print("\n🧪 TEST 4: Paginación")
    print("=" * 60)

    tester = OrderStateLogicTester()
    tester.items_per_page = 3

    # Crear 10 órdenes
    tester.all_orders = [
        {'order_number': str(i), 'status': 'Entregado', 'total': f'${i*100}', 'purchase_date': f'01/01/2025'}
        for i in range(1, 11)
    ]

    # Página 1
    tester.current_page = 1
    page1 = tester.get_filtered_orders()
    assert len(page1) == 3, f"❌ Página 1 debería tener 3 items, tiene {len(page1)}"
    print(f"✅ Página 1: {len(page1)} items")

    # Página 2
    tester.current_page = 2
    page2 = tester.get_filtered_orders()
    assert len(page2) == 3, f"❌ Página 2 debería tener 3 items, tiene {len(page2)}"
    assert page2[0]['order_number'] != page1[0]['order_number'], "❌ Páginas tienen los mismos items"
    print(f"✅ Página 2: {len(page2)} items (diferentes de página 1)")

    # Total
    total = tester.get_total_orders()
    assert total == 10, f"❌ Total debería ser 10, es {total}"
    print(f"✅ Total de órdenes: {total}")


def main():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 60)
    print("TESTING: Lógica de OrderState")
    print("=" * 60)

    try:
        test_filtering()
        test_search()
        test_sorting()
        test_pagination()

        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS PASARON")
        print("=" * 60)
        print("\nLa lógica de OrderState está correcta.")
        print("El State debería funcionar correctamente en Reflex.")

    except AssertionError as e:
        print(f"\n❌ TEST FALLÓ: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
