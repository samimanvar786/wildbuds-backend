from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = OrderItem
        fields = ["product_id", "name", "price", "quantity", "image"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "razorpay_order_id", "total_amount", "currency",
                  "status", "created_at", "items"]
        
    def get_image(self, obj):
        product = obj.product
        featured_img = product.get_featured_image()
        if featured_img and featured_img.image:
            return featured_img.image.url  # return featured image URL
        # fallback: return first available image
        first_img = product.images.first()
        return first_img.image.url if first_img else None