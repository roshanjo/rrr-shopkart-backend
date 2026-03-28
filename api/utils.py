from django.core.cache import cache
from .models import Product

def validate_cart(items, lock=False):
    """
    Validates cart items against database Products with optional caching.
    Returns: Dict with 'valid_items' and 'removed_items'
    """
    valid_items = []
    removed_items = []

    for item in items:
        product_id = item.get("product_id")
        quantity = item.get("quantity")

        if product_id is None or quantity is None:
            # Skip invalid formats silently or log? 
            # User wants self-healing, skipping is best.
            continue

        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        if quantity < 1:
            removed_items.append({"product_id": product_id, "reason": "invalid_quantity"})
            continue

        # Fetch Product
        query = Product.objects
        if lock:
            query = query.select_for_update()

        product = query.filter(id=product_id).first()
        exists = product is not None

        # Structured Logging (As requested by DEBUG requirements)
        import logging
        log = logging.getLogger(__name__)
        log.warning(
            f"[CartValidation] ID={product_id} Exists={exists} "
            f"Active={product.is_active if exists else 'N/A'} "
            f"Stock={product.stock if exists else 'N/A'} "
            f"Qty={quantity}"
        )

        # 1. Non-existent product
        if not product:
            removed_items.append({"product_id": product_id, "reason": "deleted"})
            continue

        # 2. Inactive product
        if not product.is_active:
            removed_items.append({"product_id": product_id, "reason": "inactive", "title": product.title})
            continue

        # 3. Out of stock
        if product.stock <= 0:
            removed_items.append({"product_id": product_id, "reason": "out_of_stock", "title": product.title})
            continue

        # 4. Quantity adjustment
        if quantity > product.stock:
            removed_items.append({
                "product_id": product_id, 
                "reason": "quantity_adjusted", 
                "title": product.title,
                "original_qty": quantity,
                "new_qty": product.stock
            })
            quantity = product.stock

        # 5. Valid Item
        valid_items.append({
            "product": product,
            "quantity": quantity,
            "price_inr": product.price_inr
        })

    return {
        "valid_items": valid_items,
        "removed_items": removed_items
    }
