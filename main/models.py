from django.db import models
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    # Note: keep schema compatible with existing migrations (no created_at column yet)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x{self.quantity} ({self.user})"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # keep existing DB field 'total' (added in migrations) and provide a
    # `total_price` property for templates/admin compatibility
    total = models.IntegerField(default=0)
    # shipping / order info
    recipient_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    # approval metadata
    approved_at = models.DateTimeField(blank=True, null=True)
    review_note = models.TextField(blank=True, null=True)

    @property
    def total_price(self):
        return self.total

    def __str__(self):
        return f"Order #{self.id} - {self.user} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField(help_text='Price at time of purchase')

    def __str__(self):
        return f"{self.product} x{self.quantity}"
