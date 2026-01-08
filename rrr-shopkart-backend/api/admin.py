from django.contrib import admin
from .models import User, Order

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total", "created_at")


