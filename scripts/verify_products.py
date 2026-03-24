from api.models import Product

def verify():
    ids = [1, 8, 160, 194] # Max synced is 194 products
    found = []
    missing = []
    
    for i in ids:
        p = Product.objects.filter(id=i).first()
        if p:
            found.append(f"Product #{i}: {p.title}")
        else:
            missing.append(f"Product #{i}")
            
    print("Found:")
    for f in found:
        print(f)
        
    print("\nMissing:")
    for m in missing:
        print(m)
        
    print(f"\nTotal count in DB: {Product.objects.count()}")

verify()
