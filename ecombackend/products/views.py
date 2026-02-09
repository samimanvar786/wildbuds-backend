from django.shortcuts import render
from rest_framework.decorators import action,api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import viewsets
from datetime import timedelta
from django.utils.timezone import now
from .models import Category,Product,Order
from .serializers import CategorySerializer, ProductSerializer,ShopByCategorySerializer,CategoryWithProductsSerializer,OrderSerializer

    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Retrieve all products for the selected category."""
        category = self.get_object()  # Get the specific category object
        products = Product.objects.filter(category=category)  # Filter products by category
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)    

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # 1. Endpoint to retrieve a product by its slug
    @action(detail=False, methods=['get'], url_path='shop/(?P<slug>[-\w]+)')
    def product_detail_by_slug(self, request, slug=None):
        """
        Retrieve a product by its slug.
        """
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    # 2. Endpoint to retrieve featured products
    @action(detail=False, methods=['get'], url_path='featured')
    def featured_products(self, request):
        """
        Retrieve all featured products.
        """
        featured_products = Product.objects.filter(is_featured=True)
        if not featured_products.exists():
            return Response({"detail": "No featured products available."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'], url_path='new')
    def new_products(self, request):
        """
        Retrieve products created in the last 30 days.
        """
        # Define the time range for "new" products (last 30 days)
        time_threshold = now() - timedelta(days=30)
        
        # Filter products by `created_at`
        new_products = Product.objects.filter(created_at__gte=time_threshold)
        
        # Check if there are any new products
        if not new_products.exists():
            return Response({"detail": "No new products available."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize and return the new products
        serializer = self.get_serializer(new_products, many=True)
        return Response(serializer.data)

   
    
# class CategoryViewSet(viewsets.ModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer

#     @action(detail=True, methods=['get'], url_path='products')
#     def get_category_products(self, request, pk=None):
#         """Retrieve all products under a specific category."""
#         category = self.get_object()  # Retrieve the category based on pk
#         products = Product.objects.filter(category=category)
        
#         if not products.exists():
#             return Response({"detail": "No products found for this category."}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = ProductSerializer(products, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)
        
#     @action(detail=False, methods=['get'], url_path='shop-by-category')
#     def shop_by_category(self, request):
#         """Retrieve the 8 most recent categories for 'Shop By Category' (without product details)."""
#         categories = Category.objects.order_by('-id')[:8]  # Fetch last 8 categories
#         serializer = ShopByCategorySerializer(categories, many=True, context={'request': request})
#         return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        """
        Use `CategoryWithProductsSerializer` for single-category requests,
        otherwise, use `CategorySerializer` for category listings.
        """
        if self.action == 'retrieve' or self.action == 'category_detail_by_name':
            return CategoryWithProductsSerializer
        return CategorySerializer

    @action(detail=False, methods=['get'], url_path='(?P<slug>[-\w]+)')
    def category_detail_by_name(self, request, slug=None):
        """
        Retrieve a category by its name along with related products.
        """
        try:
            category = Category.objects.get(slug__iexact=slug)  # Case-insensitive match
            serializer = CategoryWithProductsSerializer(category, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'detail': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
        
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'], url_path='(?P<slug>[-\w]+)')
    def product_detail(self, request, slug=None):
        """
        Retrieve detailed information about a product by its slug.
        """
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response({"message": "Order placed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)