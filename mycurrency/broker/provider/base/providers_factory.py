from typing import List, Union

from broker.provider.fixer_provider import FixerProvider
from main.constants import FIXER_PROVIDER_NAME
from rest_framework import status

from main.error_messages import EPROVIDER_000002, MyCurrencyError


class CurrencyExchangeRateProviderFactory:
    def get_exchange_provider(
        self, provider: str, code_list: List[str]
    ) -> Union["FixerProvider"]:
        provider: Union["FixerProvider"] = self._get_provider(
            provider=provider, code_list=code_list
        )
        return provider

    def _get_provider(
        self, code_list: List[str], provider: str = FIXER_PROVIDER_NAME
    ) -> Union["FixerProvider"]:
        if provider == FIXER_PROVIDER_NAME:
            return FixerProvider(code_list=code_list)

        raise MyCurrencyError(
            errors=EPROVIDER_000002, status_code=status.HTTP_400_BAD_REQUEST
        )
