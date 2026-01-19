"""
Servicio POO para gestión de tasas de cambio.
Permite conversión entre monedas usando tasas fijas de la compañía.

Principios aplicados: KISS, DRY, YAGNI, POO
"""

import sqlmodel
from typing import Optional
from datetime import datetime, timezone

from database.exchange_rates import ExchangeRates


class ExchangeService:
    """
    Servicio POO para conversión de monedas.
    Principio POO: Encapsula lógica de conversión de divisas.
    """

    # Monedas soportadas por país
    COUNTRY_CURRENCIES = {
        "Mexico": "MXN",
        "USA": "USD",
        "Colombia": "COP"
    }

    @classmethod
    def convert_amount(
        cls,
        session,
        amount: float,
        from_currency: str,
        to_currency: str,
        as_of_date: Optional[datetime] = None
    ) -> float:
        """
        Convierte un monto de una moneda a otra usando tasas de la compañía.
        Principio KISS: Conversión directa usando tabla de tasas.

        Args:
            session: Sesión de base de datos
            amount: Monto a convertir
            from_currency: Moneda origen (MXN, USD, COP)
            to_currency: Moneda destino (MXN, USD, COP)
            as_of_date: Fecha para tasa vigente (default: ahora)

        Returns:
            Monto convertido en moneda destino
        """
        try:
            # Si son la misma moneda, retornar el mismo monto
            if from_currency == to_currency:
                return amount

            # Fecha de referencia
            if as_of_date is None:
                as_of_date = datetime.now(timezone.utc)

            # Buscar tasa de cambio vigente
            rate = cls._get_exchange_rate(session, from_currency, to_currency, as_of_date)

            if rate is None:
                print(f"⚠️  No se encontró tasa {from_currency} -> {to_currency}, usando 1:1")
                return amount

            return amount * rate

        except Exception as e:
            print(f"❌ Error convirtiendo {amount} {from_currency} -> {to_currency}: {e}")
            return amount

    @classmethod
    def _get_exchange_rate(
        cls,
        session,
        from_currency: str,
        to_currency: str,
        as_of_date: datetime
    ) -> Optional[float]:
        """
        Obtiene la tasa de cambio vigente para una fecha específica.
        Principio DRY: Lógica centralizada de búsqueda de tasas.

        Args:
            session: Sesión de base de datos
            from_currency: Moneda origen
            to_currency: Moneda destino
            as_of_date: Fecha de referencia

        Returns:
            Tasa de cambio o None si no existe
        """
        try:
            # Buscar tasa vigente
            exchange_rate = session.exec(
                sqlmodel.select(ExchangeRates)
                .where(
                    (ExchangeRates.from_currency == from_currency) &
                    (ExchangeRates.to_currency == to_currency) &
                    (ExchangeRates.effective_from <= as_of_date) &
                    (
                        (ExchangeRates.effective_until.is_(None)) |
                        (ExchangeRates.effective_until >= as_of_date)
                    )
                )
                .order_by(sqlmodel.desc(ExchangeRates.effective_from))
            ).first()

            return exchange_rate.rate if exchange_rate else None

        except Exception as e:
            print(f"❌ Error obteniendo tasa {from_currency} -> {to_currency}: {e}")
            return None

    @classmethod
    def get_country_currency(cls, country_cache: str) -> str:
        """
        Obtiene el código de moneda para un país.
        Principio KISS: Mapeo simple.

        Args:
            country: Nombre del país

        Returns:
            Código de moneda (MXN, USD, COP)
        """
        return cls.COUNTRY_CURRENCIES.get(country_cache, "MXN")

    @classmethod
    def create_exchange_rate(
        cls,
        session,
        from_currency: str,
        to_currency: str,
        rate: float,
        effective_from: Optional[datetime] = None,
        effective_until: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Crea una nueva tasa de cambio en el sistema.
        Principio POO: Método factory para crear tasas.

        Args:
            session: Sesión de base de datos
            from_currency: Moneda origen
            to_currency: Moneda destino
            rate: Tasa de conversión
            effective_from: Fecha inicio de vigencia (default: ahora)
            effective_until: Fecha fin de vigencia (default: indefinido)
            notes: Notas adicionales

        Returns:
            ID de la tasa creada o None si falla
        """
        try:
            if effective_from is None:
                effective_from = datetime.now(timezone.utc)

            exchange_rate = ExchangeRates(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=rate,
                effective_from=effective_from,
                effective_until=effective_until,
                notes=notes
            )

            session.add(exchange_rate)
            session.flush()

            print(f"✅ Tasa de cambio creada: 1 {from_currency} = {rate} {to_currency}")
            return exchange_rate.id

        except Exception as e:
            print(f"❌ Error creando tasa de cambio: {e}")
            return None
