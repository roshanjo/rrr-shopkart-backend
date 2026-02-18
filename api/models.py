from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self):
        return self.user.username


# ============================
# Order Model
# ============================

class Order(models.Model):

    # A user can have multiple orders
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    items = models.JSONField()

    total = models.IntegerField()

    stripe_session_id = models.CharField(
        max_length=255,
        unique=True
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