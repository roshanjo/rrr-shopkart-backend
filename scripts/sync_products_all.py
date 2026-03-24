import requests
from api.models import Product

def sync():
    count = 0
    print("Syncing products by iterating IDs 1 through 200...")
    for i in range(1, 201):
        try:
            url = f"https://dummyjson.com/products/{i}"
            resp = requests.get(url, timeout=2) # 2s is plenty for individual
            if resp.status_code == 200:
                p = resp.json()
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
        except Exception:
            pass
            
    print(f"Successfully synced {count} products individually.")

if __name__ == "__main__":
    sync()
