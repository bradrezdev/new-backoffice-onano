import reflex as rx
from typing import List, Dict, Any, Optional
from sqlmodel import select, desc
from datetime import datetime

from ...auth.state.auth_state import AuthState
from ..backend.wallet_service import WalletService
from database.wallet import WalletWithdrawals, Wallets

class FinanceState(rx.State):
    """Estado para el módulo de Finanzas."""

    withdrawals_list: List[Dict[str, Any]] = []
    balance: float = 0.0
    currency: str = "USD"
    
    # Dashboard Metrics
    total_withdrawn: float = 0.0
    count_completed: int = 0
    count_pending: int = 0
    count_rejected: int = 0

    @rx.var
    def total_withdrawn_formatted(self) -> str:
        return f"{self.total_withdrawn:,.2f}"

    # Form fields for new withdrawal
    amount_to_withdraw: str = ""
    bank_name: str = ""
    account_number: str = ""
    account_holder_name: str = ""

    async def load_balance(self):
        auth_state = await self.get_state(AuthState)
        user_data = auth_state.logged_user_data
        member_id = user_data.get("member_id")
        if member_id:
            with rx.session() as session:
                wallet = session.exec(select(Wallets).where(Wallets.member_id == member_id)).first()
                if wallet:
                    self.balance = wallet.balance
                    self.currency = wallet.currency
                else:
                    self.balance = 0.0
                    self.currency = "USD"

    async def load_withdrawals(self):
        auth_state = await self.get_state(AuthState)
        user_data = auth_state.logged_user_data
        member_id = user_data.get("member_id")
        if member_id:
            with rx.session() as session:
                withdrawals = session.exec(
                    select(WalletWithdrawals)
                    .where(WalletWithdrawals.member_id == member_id)
                    .order_by(desc(WalletWithdrawals.requested_at))
                ).all()
                self.withdrawals_list = [self._map_withdrawal(w) for w in withdrawals]
                
                # Calculate metrics
                self.total_withdrawn = 0.0
                self.count_completed = 0
                self.count_pending = 0
                self.count_rejected = 0
                
                for w in withdrawals:
                    if w.status == "COMPLETED":
                        self.count_completed += 1
                        self.total_withdrawn += float(w.amount)
                    elif w.status in ["PENDING", "PROCESSING"]:
                        self.count_pending += 1
                    elif w.status == "REJECTED":
                        self.count_rejected += 1

    def _map_withdrawal(self, w: WalletWithdrawals) -> Dict[str, Any]:
        return {
            "id": f"WD{w.id:03d}" if w.id else "WD---",
            "method": f"{w.bank_name} - {w.account_number[-4:] if w.account_number else '****'}",
            "amount": f"{w.amount:,.2f}",
            "date": w.requested_at.strftime("%Y-%m-%d") if w.requested_at else "",
            "status": w.status
        }
    
    async def on_load(self):
        await self.load_balance()
        await self.load_withdrawals()

    async def submit_withdrawal(self):
        auth_state = await self.get_state(AuthState)
        user_data = auth_state.logged_user_data
        member_id = user_data.get("member_id")
        
        if not member_id:
            return rx.window_alert("Error: Usuario no identificado")
            
        try:
            amount = float(self.amount_to_withdraw)
        except ValueError:
            return rx.window_alert("Monto inválido")
            
        if amount <= 0:
             return rx.window_alert("El monto debe ser mayor a 0")
        
        # Validación básica de campos bancarios
        if not self.bank_name or not self.account_number or not self.account_holder_name:
            return rx.window_alert("Por favor complete todos los datos bancarios")

        with rx.session() as session:
             # Obtener moneda de la wallet
             currency = "USD"
             wallet = session.exec(select(Wallets).where(Wallets.member_id == member_id)).first()
             if wallet:
                 currency = wallet.currency

             result = WalletService.request_withdrawal(
                 session=session,
                 member_id=member_id,
                 amount=amount,
                 currency=currency,
                 bank_name=self.bank_name,
                 account_number=self.account_number,
                 account_holder_name=self.account_holder_name
             )
             
             if result:
                 self.load_balance()
                 self.load_withdrawals()
                 # Reset fields
                 self.amount_to_withdraw = ""
                 self.bank_name = ""
                 self.account_number = ""
                 self.account_holder_name = ""
                 return rx.window_alert("Solicitud enviada con éxito")
             else:
                 return rx.window_alert("No se pudo procesar el retiro (verifique su saldo)")
