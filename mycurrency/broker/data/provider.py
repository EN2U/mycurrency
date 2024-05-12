from typing import List

from django.db import IntegrityError
from broker.models import Provider as ProviderORM
from broker.models import ProviderTimeoutQuerySet
from django.db.models import QuerySet

from broker.serialization.entity.provider import ProviderEntity
from broker.serialization.dto.provider import ProviderCreateDTO
from rest_framework import status

from main.error_messages import EPROVIDER_DB_000001, MyCurrencyError


class ProviderRepository:
    def retrieve(self) -> List[ProviderEntity]:
        provider_queryset: ProviderTimeoutQuerySet[ProviderORM] = (
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
        try:
            ProviderORM.objects.bulk_create(
                [
                    ProviderORM(
                        name=provider.name, priority_order=provider.priority_order
                    )
                    for provider in new_providers
                ]
            )
        except IntegrityError:
            raise MyCurrencyError(
                message="One or more of the provided providers already exist.",
                errors=EPROVIDER_DB_000001,
                status_code=status.HTTP_409_CONFLICT,
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
