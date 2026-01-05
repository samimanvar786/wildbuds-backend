from django.db import models
from django.conf import settings  # To link order to logged-in user

# class Payment(models.Model):
#     user_id = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
#     order_id = models.CharField(max_length=100)
#     payment_id = models.CharField(max_length=100, null=True, blank=True)
#     signature = models.CharField(max_length=255, null=True, blank=True)
#     amount = models.IntegerField()  # in paise
#     currency = models.CharField(max_length=10, default="INR")
#     status = models.CharField(max_length=20, default="created")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.order_id


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    total_amount = models.IntegerField()  # paise
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, default="created")
    tracking = models.CharField(max_length=100, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.razorpay_order_id


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.IntegerField()
    name = models.CharField(max_length=255)
    price = models.IntegerField()      # rupees
    quantity = models.IntegerField()

# class Order(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
#     razorpay_order_id = models.CharField(max_length=100, unique=True)
#     total_amount = models.IntegerField()  # paise
#     currency = models.CharField(max_length=10, default="INR")
#     status = models.CharField(max_length=20, default="created")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.razorpay_order_id


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.IntegerField()
    name = models.CharField(max_length=255)
    price = models.FloatField()  # in ₹
    quantity = models.IntegerField()

    def __str__(self):
        return self.name    