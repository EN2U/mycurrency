import csv

from typing import Any, List
from django.core.management.base import BaseCommand, CommandParser

from broker.serialization.dto.provider import ProviderCreateDTO
from django.db import transaction

from broker.core.provider import ProviderService


class Command(BaseCommand):
    help = "Command to update providers"

    def __init__(self, *args, **kwargs) -> None:
        self._provider_service = ProviderService()

        super().__init__(*args, **kwargs)

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "csvfile",
            type=open,
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("###### Updating Providers Priority ######")

        reader = csv.DictReader(options.pop("csvfile"))
        rows = list(reader)

        new_providers: List[ProviderCreateDTO] = [
            ProviderCreateDTO(name=row["name"], priority_order=row["priority_order"])
            for row in rows
        ]

        try:
            with transaction.atomic():
                self._provider_service.delete_all()
                self._provider_service.create_multiple(new_providers=new_providers)

        except Exception as e:
            print(f"Error trying to update providers: {e}")

        self.stdout.write("###### Update successfully ######")
