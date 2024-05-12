from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Union

from currency_exchange.serialization.dto.currency_exchange_rate import (
    CurrencyExchangeRateCreateDTO,
)


class CurrencyExchangeRateOperations:
    def find_missing_dates(
        self,
        current_date_list: List[date],
        start_date: date,
        end_date: date,
    ) -> List[date]:
        all_dates = set(
            str(start_date + timedelta(days=i))
            for i in range((end_date - start_date).days + 1)
        )

        saved_dates = set(current_date_list)

        missing_dates = all_dates - saved_dates

        return [datetime.strptime(date, "%Y-%m-%d").date() for date in missing_dates]

    def calculate_exchange_rates_conversions(
        self, data: Dict[str, Union[str, Dict[str, Decimal]]]
    ) -> List[CurrencyExchangeRateCreateDTO]:
        rates = data["rates"]
        current_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        exchange_rates = set()

        print(rates)
        for source_currency, source_value in rates.items():
            for target_currency, target_value in rates.items():

                if source_currency != target_currency:
                    self._add_exchange_rate(
                        first_rate=source_value,
                        second_rate=target_value,
                        first_currency=source_currency,
                        second_currency=target_currency,
                        exchange_rates=exchange_rates,
                        valuation_date=current_date,
                    )

                    self._add_exchange_rate(
                        first_rate=target_value,
                        second_rate=source_value,
                        first_currency=target_currency,
                        second_currency=source_currency,
                        exchange_rates=exchange_rates,
                        valuation_date=current_date,
                    )

        return [
            CurrencyExchangeRateCreateDTO(
                valuation_date=date,
                source_currency=source_rate,
                target_currency=target_rate,
                rate_value=value,
            )
            for date, source_rate, target_rate, value in exchange_rates
        ]

    def _add_exchange_rate(
        self,
        first_rate: Decimal,
        second_rate: Decimal,
        first_currency: str,
        second_currency: str,
        exchange_rates: set,
        valuation_date: date,
    ):
        rate = (second_rate / first_rate).quantize(Decimal("1.000000"))
        exchange_rates.add((valuation_date, first_currency, second_currency, rate))
