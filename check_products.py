import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from api.models import Product
from django.db.models import Count, Q

stats = Product.objects.values("category").annotate(
    total=Count("id"),
    inactive=Count("id", filter=Q(is_active=False)),
    zero_stock=Count("id", filter=Q(stock=0))
)

print(f"{'Category':<20} | {'Total':<5} | {'Inactive':<8} | {'Zero Stock':<10}")
print("-" * 50)
for s in stats:
    print(f"{s['category']:<20} | {s['total']:<5} | {s['inactive']:<8} | {s['zero_stock']:<10}")
