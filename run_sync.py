import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from api.models import Product
import requests

def sync():
    try:
        url = "https://dummyjson.com/products?limit=200"
        print(f"Fetching products from {url}...")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products", [])
        
        count = 0
        for p in products:
            product, created = Product.objects.update_or_create(
                id=p["id"],
                defaults={
                    "title": p["title"],
                    "price_inr": round(p.get("price", 0) * 80),
                    "category": p.get("category", ""),
                    "stock": p.get("stock", 10)
                }
            )
            count += 1
            
        print(f"Successfully synced {count} products.")
        
    except Exception as e:
        print(f"Sync failed: {str(e)}")

if __name__ == "__main__":
    sync()
