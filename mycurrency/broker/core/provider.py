from decimal import Decimal
from typing import Dict, List, Union
from broker.data.provider import ProviderRepository
from broker.serialization.entity.provider import ProviderEntity
from broker.provider.base.base_providers import CurrencyExchangeRateProvider
from broker.provider.base.providers_factory import (
    CurrencyExchangeRateProviderFactory,
)
from broker.serialization.dto.provider import ProviderCreateDTO, ProviderRetrieveDTO
from main.error_messages import EPROVIDER_000001, MyCurrencyError
from rest_framework import status


class ProviderService:
    def __init__(self, *args, **kwargs) -> None:
        self._provider_repository = ProviderRepository()
        self._provider_factory = CurrencyExchangeRateProviderFactory()

    def retrieve(self, provider_retrieve_dto: ProviderRetrieveDTO):
        provider_entity_list: List[ProviderEntity] = (
            self._provider_repository.retrieve()
        )

        response = {}

        if not provider_entity_list:

            raise MyCurrencyError(
                message="Providers not available in this moment",
                errors=EPROVIDER_000001,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        for provider_entity in provider_entity_list:
            exchange_provider: Union[CurrencyExchangeRateProvider] = (
                self._provider_factory.get_exchange_provider(
                    provider=provider_entity.name,
                    code_list=provider_retrieve_dto.code_list,
                )
            )

            try:
                response: Dict[str, Union[str, Dict[str, Decimal]]] = (
                    exchange_provider.get_currency_exchange_rate_by_date(
                        current_date=provider_retrieve_dto.current_date
                    )
                )
            except Exception as e:
                print("Something Unexpected happened, setting timeout: ", str(e))
                self._provider_repository.set_timeout(uuid=provider_entity.uuid)
                continue

            break
        return response

    def delete_all(self) -> None:
        self._provider_repository.delete_all()

    def create_multiple(self, new_providers: ProviderCreateDTO) -> List[ProviderEntity]:
        return self._provider_repository.create_multiple(new_providers=new_providers)
