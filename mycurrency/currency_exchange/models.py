from django.db import models
from django.utils.translation import gettext_lazy as _

from main.base_models import CodeBaseModel


class Currency(CodeBaseModel):
    symbol = models.CharField(max_length=10)

    class Meta(CodeBaseModel.Meta):
        db_table = "currency"
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")


class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(
        Currency, related_name="source_currency", on_delete=models.CASCADE
    )
    target_currency = models.ForeignKey(
        Currency, related_name="target_currency", on_delete=models.CASCADE
    )

    valuation_date = models.DateField(db_index=True)

    rate_value = models.DecimalField(db_index=True, decimal_places=6, max_digits=18)

    class Meta:
        db_table = "currency_exchange_rate"
        verbose_name = _("Currency exchange rate")
        verbose_name_plural = _("Currency exchange rates")


class CurrencyExchangeManager(models.Manager):
    pass
