from django.contrib import admin

from .models import Currency, CurrencyExchangeRate


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "symbol"]


class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "uuid",
        "source_currency_code",
        "target_currency_code",
        "valuation_date",
        "rate_value",
    ]

    search_fields = ["uuid"]
    list_filter = ["source_currency__code", "target_currency__code"]
    list_select_related = ["source_currency", "target_currency"]

    @admin.display(ordering="source_currency__code")
    def source_currency_code(self, obj):
        return obj.source_currency.code

    @admin.display(ordering="source_currency__code")
    def target_currency_code(self, obj):
        return obj.target_currency.code


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(CurrencyExchangeRate, CurrencyExchangeRateAdmin)
