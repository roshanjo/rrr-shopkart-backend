import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Product

try:
    print("Product Count:", Product.objects.count())
    print("All Products:")
    for p in Product.objects.all():
        print(f"ID: {p.id}, Title: {p.title}, Price: {p.price_inr}")
except Exception as e:
    print("ERROR OCCURRED:", str(e))
