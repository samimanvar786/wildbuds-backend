from django.db import models
from django.utils.text import slugify
from django.conf import settings
import os
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Name is now unique
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="categories")
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            self.slug = unique_slug
        super().save(*args, **kwargs)   

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    slug = models.SlugField(max_length=255, unique=True, blank=True)  # Slug is auto-generated if blank
    is_featured = models.BooleanField(default=False)
    is_best_seller=models.BooleanField(default=False)
    description = models.TextField()
    features = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super(Product, self).save(*args, **kwargs)

    def get_featured_image(self):
        """Get the featured image for the product."""
        return self.images.filter(is_featured=True).first()
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    # image = models.ImageField(upload_to="products")
    image = models.ImageField(
        upload_to="products",
        default=os.path.join(settings.MEDIA_URL, "defaults/default-product.png")
    )
    
    is_featured = models.BooleanField(default=False)  # New field to mark the featured image

    def save(self, *args, **kwargs):
        # Mark the first image as the featured image if none exists yet
        if self.product.images.count() == 0:
            self.is_featured = True  # Set the first image as featured
        super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"


class OrderItem(models.Model):
    """
    Model to track product sales.
    """
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="order_items")
    quantity=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    

class Order(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    order_notes = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.first_name} {self.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", default=1)  # 👈 Add default
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"