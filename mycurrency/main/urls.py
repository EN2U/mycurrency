from django.contrib import admin
from django.urls import path, include
from currency_exchange.drf.urls import urlpatterns as currency_exchange_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/currency_exchange/", include(currency_exchange_urls)),
]
