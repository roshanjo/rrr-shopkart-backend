from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


# ============================
# Profile Model
# ============================

class Profile(models.Model):

    # One profile per user
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    avatar = models.CharField(
        max_length=255,
        blank=True
    )

    theme = models.CharField(
        max_length=10,
        default="light"
    )

    status = models.CharField(
        max_length=20,
        default="active",
        choices=[
            ("active", "Active"),
            ("blocked", "Blocked"),
            ("suspended", "Suspended"),
            ("banned", "Banned"),
            ("deleted", "Deleted"),
        ]
    )

    def __str__(self):
        return self.user.username


# ============================
# ActivityLog Model
# ============================

class ActivityLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.action} @ {self.timestamp}"



# ============================
# Order Model
# ============================

class Order(models.Model):

    # A user can have multiple orders
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    items = models.JSONField()

    total = models.IntegerField()

    stripe_session_id = models.CharField(
        max_length=255,
        unique=True
    )

    payment_status = models.CharField(
        max_length=20,
        default="pending"
    )

    payment_method = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


# ============================
# Address Model
# ============================

class Address(models.Model):

    # One address per user
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=15
    )

    street = models.TextField()

    city = models.CharField(
        max_length=50
    )

    state = models.CharField(
        max_length=50
    )

    pincode = models.CharField(
        max_length=10
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.city}"


# ============================
# Product Model (Price Source of Truth)
# ============================

class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    price_inr = models.IntegerField(help_text="Price in INR")
    category = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(default=10, help_text="Stock Quantity")
    is_active = models.BooleanField(default=True, help_text="Product Visibility/Availability")

    def __str__(self):
        return f"{self.title} (₹{self.price_inr})"


# ============================
# CartSnapshot Model
# ============================

class CartSnapshot(models.Model):
    stripe_session_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )
    items = models.JSONField()  # [{product_id, quantity}]
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return f"Snapshot - {self.stripe_session_id}"
