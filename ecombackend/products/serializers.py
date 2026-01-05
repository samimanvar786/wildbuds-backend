from rest_framework import serializers
from .models import Category, Product, ProductImage,Order,OrderItem
from products.models import Product
from django.conf import settings
import os


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image']
        
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_featured']  # Ensure valid fields


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description','features', 'price','sale_price','weight', 'in_stock', 'category', 'is_featured', 'images', 'featured_image']

    def get_featured_image(self, obj):
        """Get the featured image URL if available."""
        featured_image = obj.get_featured_image()
        if featured_image:
            return self.context['request'].build_absolute_uri(featured_image.image.url)
        return None
    


class CategoryWithProductsSerializer(serializers.ModelSerializer):
    """Serializer for a single category with its related products"""
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'products']
        
class ShopByCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'description']

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'total']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'last_name', 'address', 'city', 'country', 
                  'postcode', 'phone', 'email', 'order_notes', 'total_price', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product = item_data['product']
            item_data['order'] = order
            OrderItem.objects.create(**item_data)

        return order