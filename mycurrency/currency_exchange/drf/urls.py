from django.urls import path
from rest_framework import routers
from .views import CurrencyExchangeViewSet

router = routers.DefaultRouter()

router.register(r"", CurrencyExchangeViewSet, basename="currency_exchange")


urlpatterns = router.urls
