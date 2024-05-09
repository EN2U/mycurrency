from rest_framework import serializers

from main.constants import FIXER_PROVIDER_NAME, PROVIDER_NAME


class CurrencyResponse(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=20)
    symbol = serializers.CharField(max_length=10)


class CurrencyExchangeTimeseriesRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(format="%Y-%m-%d", required=True)
    end_date = serializers.DateField(format="%Y-%m-%d", required=True)
    provider = serializers.CharField(
        required=False,
    )

    def validate_provider(self, value):
        if value not in PROVIDER_NAME:
            raise serializers.ValidationError("Proveedor no válido")
        return value


class CurrencyExchangeRateResponseSerializer(serializers.Serializer):
    source_currency = CurrencyResponse(read_only=True)
    target_currency = CurrencyResponse(read_only=True)
    valuation_date = serializers.DateField()
    rate_value = serializers.DecimalField(max_digits=18, decimal_places=6)
