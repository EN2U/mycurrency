from enum import Enum


class MyCurrencyError(Exception):
    def __init__(self, message, errors, status_code, data={}):
        super().__init__(message)

        self.errors = errors
        self.status_code = status_code
        self.message = message
        self.data = data


# CURRENCY_EXCHANGE

ECURRENCY_EXCHANGE_RATE_000001 = "Currency Error"
ECURRENCY_EXCHANGE_RATE_000002 = "Exchange Rate Not Found"
ECURRENCY_EXCHANGE_RATE_000003 = "Invalid Date Range"


ECURRENCY_EXCHANGE_RATE_DB_000001 = "Conflict creating Currency Exchange Rates"

# BROKER

EPROVIDER_000001 = "Timeout"
EPROVIDER_000002 = "Unsupported provider"

EPROVIDER_DB_000001 = "Conflict creating provider"
