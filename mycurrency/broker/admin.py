from django.contrib import admin

from broker.models import Provider

# Register your models here.


class ProviderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "uuid",
        "name",
        "priority_order",
        "timeout",
    ]

    search_fields = ["uuid", "name", "priority_order"]
    list_filter = ["priority_order", "name"]


admin.site.register(Provider, ProviderAdmin)
