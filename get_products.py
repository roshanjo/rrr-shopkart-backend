import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from api.models import Product

products = Product.objects.all()[:10]
for p in products:
    print(f"ID: {p.id}, Title: {p.title}, Stock: {p.stock}, Active: {p.is_active}")
