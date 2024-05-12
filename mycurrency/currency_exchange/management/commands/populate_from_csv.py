import csv
import ast
from decimal import Decimal
from typing import Any, Dict, List, Optional
from django.core.management.base import BaseCommand, CommandParser
from currency_exchange.utils import CurrencyExchangeRateOperations
from currency_exchange.core.services.currency_exchange_rate import (
    CurrencyExchangeRateService,
)
from currency_exchange.serialization.dto.currency_exchange_rate import (
    CurrencyExchangeRateCreateDTO,
)
from currency_exchange.core.services.currency import CurrencyService


class Command(BaseCommand):
    help = "Command to upload new currency exchange rates"

    def __init__(self, *args, **kwargs) -> None:
        self._currency_exchange_rate_operations = CurrencyExchangeRateOperations()
        self._currency_exchange_rate_service = CurrencyExchangeRateService()
        self._currency_service = CurrencyService()

        super().__init__(*args, **kwargs)

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "csvfile",
            type=open,
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("###### Importing Currency Exchange Rates ######")

        reader = csv.DictReader(options.pop("csvfile"))
        rows = list(reader)

        self._check_duplicated_dates(rows=rows)

        new_currency_exchange_rate_list_dto: List[CurrencyExchangeRateCreateDTO] = []
        for row in rows:
            rates_dict: Dict[str, str] = ast.literal_eval(row["rates"])

            self._check_valid_currencies(
                currency_codes_db=set(
                    [currency.code for currency in self._currency_service.retrieve()]
                ),
                currency_codes_row=set(rates_dict.keys()),
            )

            new_currency_exchange_rate_list_dto.extend(
                self._currency_exchange_rate_operations.calculate_exchange_rates_conversions(
                    data={
                        "date": row["valuation_date"],
                        "rates": {
                            currency: Decimal(rate)
                            for currency, rate in rates_dict.items()
                        },
                    }
                )
            )
        self._currency_exchange_rate_service.create_multiple(
            new_currency_exchange_rate_list_dto=new_currency_exchange_rate_list_dto
        )

    def _check_duplicated_dates(self, rows: Dict[str, str]) -> None:
        dates: List[str] = [row["valuation_date"] for row in rows]

        duplicates: Optional[List[str]] = [
            date for date in dates if dates.count(date) > 1
        ]
        if duplicates:
            raise ValueError(
                f"The following dates are duplicated in CSV: {', '.join(duplicates)}"
            )

    def _check_valid_currencies(
        self, currency_codes_db: set, currency_codes_row: set
    ) -> None:
        if currency_codes_row != currency_codes_db:
            raise ValueError(
                "Invalid currencies. Check your currencies coincide with the following: "
                + ",".join(currency_codes_db)
                + "\nInvalid Currencies: "
                + ",".join(currency_codes_row - currency_codes_db)
            )
