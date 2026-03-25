from django.core.cache import cache
from .models import Product

def validate_cart(items, lock=False):
    """
    Validates cart items against database Products with optional caching.
    
    items: List of dicts, supporting ONLY keys: 'product_id' and 'quantity'
    lock: If True, uses select_for_update() inside a transaction
    
    Returns: List of dicts with full 'product' object, 'quantity', and 'price_inr'
    Raises: Exception with descriptive error if validation fails
    """
    validated_items = []

    for item in items:
        # Strict Format Enforcement
        product_id = item.get("product_id")
        quantity = item.get("quantity")

        if product_id is None or quantity is None:
            raise Exception("Invalid cart format")

        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise Exception("Invalid product data format")

        if quantity < 1:
            raise Exception("Quantity must be at least 1")

        # Safe Product Caching
        cache_key = f"product_{product_id}"
        product = None

        if not lock:
            product = cache.get(cache_key)

        if not product:
            query = Product.objects
            if lock:
                query = query.select_for_update()

            product = query.filter(id=product_id).first()

            if not product:
                raise Exception(f"Product #{product_id} no longer available")

            if product and not lock:
                cache.set(cache_key, product, 300) # 5 minutes validation

        # Stock Validation (ALWAYS fresh from DB when lock=True)
        if product.stock < 1:
            raise Exception("Out of stock")

        if quantity > product.stock:
            quantity = product.stock # CAP to available stock

        validated_items.append({
            "product": product,
            "quantity": quantity,
            "price_inr": product.price_inr
        })

    return validated_items
