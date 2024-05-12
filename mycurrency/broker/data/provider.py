from typing import List
from broker.models import Provider as ProviderORM, ProviderTimeoutQueryset
from django.db.models import QuerySet

from broker.serialization.entity.provider import ProviderEntity
from broker.serialization.dto.provider import ProviderCreateDTO


class ProviderRepository:
    def retrieve(self) -> List[ProviderEntity]:
        provider_queryset: ProviderTimeoutQueryset[ProviderORM] = (
            self._get_queryset_exclude_timeout().order_by("-priority_order")
        )

        return [self._orm_to_entity(orm=provider) for provider in provider_queryset]

    def set_timeout(self, uuid: str) -> None:
        provider: ProviderORM = self._get_provider_by_uuid(uuid=uuid)

        provider.set_timeout()

    def delete_all(self) -> None:
        self._get_queryset().delete()

    def create_multiple(
        self, new_providers: List[ProviderCreateDTO]
    ) -> List[ProviderEntity]:
        ProviderORM.objects.bulk_create(
            [
                ProviderORM(name=provider.name, priority_order=provider.priority_order)
                for provider in new_providers
            ]
        )

    def _orm_to_entity(self, orm: ProviderORM) -> ProviderEntity:
        return ProviderEntity.model_validate(orm)

    def _get_queryset_exclude_timeout(self) -> QuerySet[ProviderORM]:
        return self._get_queryset().exclude_timeout()

    def _get_queryset(self) -> QuerySet[ProviderORM]:
        return ProviderORM.objects.all()

    def _get_provider_by_uuid(self, uuid: str) -> ProviderORM:
        try:
            return ProviderORM.objects.get(uuid=uuid)
        except ProviderORM.DoesNotExist:
            raise
