import reflex as rx
from typing import List, Dict, Any

class FinanceState(rx.State):
    """Estado para el módulo de Finanzas."""
    
    withdrawals_list: List[Dict[str, Any]] = [
        {"id": "WD001", "method": "🏦 Banco Santander ****1234", "amount": 500.00, "date": "2024-09-10", "status": "Completado"},
        {"id": "WD002", "method": "💳 PayPal - usuario@email.com", "amount": 750.00, "date": "2024-09-08", "status": "Procesando"},
        {"id": "WD003", "method": "🏦 BBVA ****5678", "amount": 300.00, "date": "2024-09-05", "status": "Completado"},
        {"id": "WD004", "method": "🪙 Bitcoin - 1A2B...XY89", "amount": 1200.00, "date": "2024-09-03", "status": "Rechazado"},
        {"id": "WD005", "method": "🏦 Banco Santander ****1234", "amount": 850.00, "date": "2024-09-01", "status": "Completado"},
        {"id": "WD006", "method": "💳 PayPal - usuario@email.com", "amount": 450.00, "date": "2024-08-28", "status": "Completado"},
        {"id": "WD007", "method": "🏦 BBVA ****5678", "amount": 600.00, "date": "2024-08-25", "status": "Procesando"},
        {"id": "WD008", "method": "🪙 Bitcoin - 1A2B...XY89", "amount": 950.00, "date": "2024-08-22", "status": "Completado"},
        {"id": "WD009", "method": "🏦 Banco Santander ****1234", "amount": 350.00, "date": "2024-08-20", "status": "Completado"},
        {"id": "WD010", "method": "💳 PayPal - usuario@email.com", "amount": 700.00, "date": "2024-08-18", "status": "Completado"},
    ]
    
    
