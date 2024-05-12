from typing import List, Union

from currency_exchange.core.providers.fixer_provider import FixerProvider
from main.constants import FIXER_PROVIDER_NAME


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

        raise
