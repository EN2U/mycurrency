from rest_framework import serializers


class CurrencyResponse(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=20)
    symbol = serializers.CharField(max_length=10)


class CurrencyExchangeTimeseriesRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(format="%Y-%m-%d", required=True)
    end_date = serializers.DateField(format="%Y-%m-%d", required=True)


class CurrencyExchangeTimeseriesByCurrencyRequestSerializer(
    CurrencyExchangeTimeseriesRequestSerializer
):
    currency = serializers.CharField(required=True)


class CurrencyExchangeRateResponseSerializer(serializers.Serializer):
    source_currency = CurrencyResponse(read_only=True)
    target_currency = CurrencyResponse(read_only=True)
    valuation_date = serializers.DateField()
    rate_value = serializers.DecimalField(max_digits=18, decimal_places=6)


class CurrencyExhangeConversionRequestSerializer(serializers.Serializer):
    source_currency = serializers.CharField(required=True)
    target_currency = serializers.CharField(required=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=6)


class CurrencyExchangeConversionResponseSerializer(serializers.Serializer):
    source_currency = serializers.CharField(required=True)
    target_currency = serializers.CharField(required=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=6)
    rate_value = serializers.DecimalField(max_digits=18, decimal_places=6)


class CurrencyExchangeTWRRRequestSerializer(CurrencyExhangeConversionRequestSerializer):
    start_date = serializers.DateField(format="%Y-%m-%d", required=True)


class CurrencyExchangeRateTWRRResponseSerializer(
    CurrencyExchangeConversionResponseSerializer
):
    valuation_date = serializers.DateField(format="%Y-%m-%d", required=True)
    twrr = serializers.DecimalField(max_digits=18, decimal_places=6)
    twrr_accumulated = serializers.DecimalField(max_digits=18, decimal_places=6)
