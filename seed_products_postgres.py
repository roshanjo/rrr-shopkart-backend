import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from api.models import Product

products = [
    Product(id=1, title="Men's Denim Jacket", price_inr=2499, category="Clothing"),
    Product(id=2, title="Women's Summer Dress", price_inr=1899, category="Clothing"),
    Product(id=3, title="Organic Coffee Beans", price_inr=799, category="Food"),
    Product(id=4, title="Premium Dark Chocolate", price_inr=499, category="Food"),
    Product(id=5, title="Wireless Headphones", price_inr=5999, category="Electronics"),
    Product(id=6, title="Smart Watch Series X", price_inr=8999, category="Electronics")
]

print("Seeding products on PostgreSQL...")
Product.objects.bulk_create(products, ignore_conflicts=True)
print('Seeded Count:', Product.objects.count())
