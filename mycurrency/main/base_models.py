import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_uuid4() -> str:
    return uuid.uuid4().hex


class CodeBaseModel(models.Model):
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        abstract = True


class UUIDBaseModel(models.Model):
    uuid = models.CharField(
        verbose_name=_("UUID"),
        editable=True,
        unique=True,
        default=generate_uuid4,
        max_length=42,
    )

    class Meta:
        abstract = True

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __str__(self):
        return self.uuid
