from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _

from main.base_models import UUIDBaseModel


class ProviderTimeoutQueryset(models.QuerySet):
    def exclude_timeout(self):
        now = datetime.now()
        return self.filter(models.Q(timeout__isnull=True) | models.Q(timeout__lte=now))


class Provider(UUIDBaseModel):
    name = models.CharField(max_length=20, unique=True)
    priority_order = models.IntegerField()
    timeout = models.DateTimeField(null=True, blank=True)

    objects = ProviderTimeoutQueryset.as_manager()

    class Meta:
        db_table = "provider"
        verbose_name = _("Provider")
        verbose_name_plural = _("Providers")

    @property
    def can_search(self) -> bool:
        if self.timeout is None:
            return True

        now = datetime.now()
        return now >= self.timeout

    def set_timeout(self):
        self.timeout = datetime.now() + timedelta(hours=8)
        self.save(update_fields=["timeout"])
