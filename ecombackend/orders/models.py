import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.db import models, transaction
from django.conf import settings
from django.utils.timezone import now


def two_dp(value):
    """Helper to round to 2dp"""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class OrderCounter(models.Model):
    """Keeps a daily sequence counter"""
    key = models.CharField(max_length=20, unique=True)  # e.g., "20250908"
    seq = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.key} -> {self.seq}"
    
class Order(models.Model):
    db_table = "orders_order"
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("returned", "Returned"),
        ("refunded", "Refunded"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    order_id = models.CharField(max_length=50, unique=True, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="customer_orders",
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="USD")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")

    shipping_address = models.JSONField(blank=True, null=True)
    billing_address = models.JSONField(blank=True, null=True)
    shipping_method = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=200, blank=True)
    order_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "orders"   # force correct app → `orders_order`

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_id(prefix="ORD"):
        from orders.models import OrderCounter
        today = now().strftime("%Y%m%d")
        with transaction.atomic():
            counter, _ = OrderCounter.objects.select_for_update().get_or_create(key=today)
            counter.seq += 1
            counter.save()
            short_uuid = uuid.uuid4().hex[:10].upper()
            return f"{prefix}-{short_uuid}-{counter.seq:05d}"
        
    def update_totals(self):
        items = self.items.all()
        subtotal = sum([(it.price * it.quantity) for it in items])
        total_discount = sum([(it.discount * it.quantity) for it in items])
        total_tax = sum([it.tax for it in items])
        self.subtotal = two_dp(subtotal)
        self.discount = two_dp(total_discount)
        self.tax = two_dp(total_tax)
        self.total_amount = two_dp(subtotal - total_discount + total_tax + self.shipping_fee)
        self.save(update_fields=["subtotal", "discount", "tax", "total_amount"])

    def __str__(self):
        return f"Order {self.order_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        "products.Product",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="order_items",
    )

    name = models.CharField(max_length=255, blank=True)
    sku = models.CharField(max_length=200, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "orders"   # force correct app → `orders_orderitem`

    def save(self, *args, **kwargs):
        if self.product and not self.name:
            self.name = self.product.name
        if self.product and not self.sku:
            self.sku = getattr(self.product, "sku", "")

        self.total = two_dp(
            (self.price * self.quantity) - (self.discount * self.quantity) + self.tax
        )
        super().save(*args, **kwargs)

        if self.order:
            self.order.update_totals()

    def __str__(self):
        return f"{self.quantity} x {self.name} (Order {self.order.order_id})"
