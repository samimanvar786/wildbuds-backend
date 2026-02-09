from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from orders.models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "name", "sku", "quantity", "price",
                  "discount", "tax", "total"]
        read_only_fields = ["id", "total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "items",
            "subtotal",
            "discount",
            "tax",
            "shipping_fee",
            "total_amount",
            "currency",
            "status",
            "payment_status",
            "shipping_address",
            "billing_address",
            "shipping_method",
            "payment_method",
            "tracking_number",
            "order_notes",
            "created_at",
        ]
        read_only_fields = ["subtotal", "discount", "tax", "total_amount", "created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        shipping_fee = validated_data.get("shipping_fee", Decimal("0.00"))
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item in items_data:
                product = item.get("product")
                price = item.get("price") or (product.price if product else Decimal("0.00"))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    name=item.get("name") or (product.name if product else ""),
                    sku=item.get("sku", ""),
                    quantity=item.get("quantity", 1),
                    price=price,
                    discount=item.get("discount", Decimal("0.00")),
                    tax=item.get("tax", Decimal("0.00")),
                )
            order.shipping_fee = shipping_fee
            order.update_totals()
        return order
