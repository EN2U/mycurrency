from django.apps import AppConfig
from django.db.backends.signals import connection_created

# from .utils import initialize_currency_exchange_db


# class CurrencyExchangeInitializer:
#     def __init__(self):
#         from .models import Currency, CurrencyExchangeRate

#         self.remaining_required_models = [Currency, CurrencyExchangeRate]
#         self.is_db_connected = False

#     def handle_initialization(self, **kwargs):
#         initialize_currency_exchange_db

#     def __fetch_exchange_data():
#         pass


# class CurrencyExchangeConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "currency_exchange"

#     def ready(self):
#         from django.db.models.signals import post_init, pre_init

#         initializer = CurrencyExchangeInitializer()

#         connection_created.connect(
#             initializer.handle_initialization, weak=False, dispatch_uid="random"
#         )

#         for model in initializer.remaining_required_models:
#             pre_init.connect(
#                 initializer.handle_initialization,
#                 sender=model,
#                 dispatch_uid=model.__name__,
#                 weak=False,
#             )


class CurrencyExchangeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "currency_exchange"
