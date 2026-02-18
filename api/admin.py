from django.contrib import admin
from .models import Profile, Order


# ============================
# Profile Admin
# ============================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    # Columns visible in Django admin panel
    list_display = (
        "id",
        "user",
        "theme",
    )


# ============================
# Order Admin
# ============================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # Columns visible in Django admin panel
    list_display = (
        "id",
        "user",
        "total",
        "created_at",
        "stripe_session_id",
    )

    # Search bar fields in admin panel
    search_fields = (
        "stripe_session_id",
        "user__username",
    )

    # Filter options in right sidebar
    list_filter = (
        "created_at",
    )