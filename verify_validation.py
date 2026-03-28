import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from api.models import Product
from api.utils import validate_cart

def test_validation():
    print("Running Validation Tests...")
    
    # Setup test products
    # 1. Normal active product
    p_active = Product.objects.create(title="Active Product", price_inr=100, stock=10, is_active=True, category="test")
    # 2. Inactive product
    p_inactive = Product.objects.create(title="Inactive Product", price_inr=100, stock=10, is_active=False, category="test")
    # 3. Out of stock product
    p_no_stock = Product.objects.create(title="No Stock Product", price_inr=100, stock=0, is_active=True, category="test")
    
    items = [
        {"product_id": p_active.id, "quantity": 2},
        {"product_id": p_inactive.id, "quantity": 1},
        {"product_id": p_no_stock.id, "quantity": 1},
        {"product_id": 9999, "quantity": 1}, # Non-existent
    ]
    
    print(f"Testing with items: {items}")
    result = validate_cart(items)
    
    valid_ids = [item["product"].id for item in result["valid_items"]]
    removed_reasons = {item["product_id"]: item["reason"] for item in result["removed_items"]}
    
    print(f"Valid IDs: {valid_ids}")
    print(f"Removed reasons: {removed_reasons}")
    
    assert p_active.id in valid_ids
    assert p_inactive.id not in valid_ids
    assert p_no_stock.id not in valid_ids
    assert 9999 not in valid_ids
    
    assert removed_reasons[p_inactive.id] == "inactive"
    assert removed_reasons[p_no_stock.id] == "out_of_stock"
    assert removed_reasons[9999] == "deleted"
    
    print("PASSED: validate_cart correctly filters items.")

    # Test Quantity adjustment
    items_qty = [{"product_id": p_active.id, "quantity": 20}]
    result_qty = validate_cart(items_qty)
    print(f"Quantity adjustment test result: {result_qty}")
    assert len(result_qty["valid_items"]) == 1, "Should have 1 valid item"
    assert result_qty["valid_items"][0]["quantity"] == 10, f"Expected quantity 10, got {result_qty['valid_items'][0]['quantity']}"
    assert len(result_qty["removed_items"]) == 1, f"Should have 1 removed item, got {len(result_qty['removed_items'])}"
    reason = result_qty["removed_items"][0]["reason"]
    print(f"Reason: {repr(reason)}")
    assert reason == "quantity_adjusted", f"Expected 'quantity_adjusted', got {repr(reason)}"
    print("PASSED: validate_cart correctly adjusts quantity.")

    # Cleanup
    p_active.delete()
    p_inactive.delete()
    p_no_stock.delete()

if __name__ == "__main__":
    try:
        test_validation()
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
