from rest_framework import serializers


class ProductSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    sku = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(min_value=0)
    low_stock_threshold = serializers.IntegerField(min_value=0, default=5)


class ProductUpdateSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    deduct_quantity = serializers.IntegerField(min_value=1, required=True)
