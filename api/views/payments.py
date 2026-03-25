import os
import stripe
import logging

logger = logging.getLogger(__name__)

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Order, Product, ActivityLog


# ==================================================
# STRIPE CONFIG
# ==================================================

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")


# ==================================================
# STRIPE CHECKOUT (SECURED)
# ==================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    try:
        items = request.data.get("items", []) # Expects list of {id, qty}

        if not items:
            return Response({"error": "Cart is empty"}, status=400)

        logger.info(f"Checkout Start for user_id={request.user.id}")

        # FIX 1: NORMALIZE CART INPUT
        items = [
            {
                "product_id": item.get("product_id") or item.get("id"),
                "quantity": item.get("quantity") or item.get("qty")
            }
            for item in items
        ]

        # FIX 2: AGGREGATE DUPLICATES
        aggregated = {}
        for item in items:
            pid = item["product_id"]
            qty = item["quantity"]
            
            if pid in aggregated:
                aggregated[pid] += qty
            else:
                aggregated[pid] = qty
                
        normalized_items = [
            {"product_id": pid, "quantity": qty}
            for pid, qty in aggregated.items()
        ]

        # Validation
        from ..utils import validate_cart
        validated = validate_cart(normalized_items, lock=False)
        valid_items = validated["valid_items"]
        removed_items = validated["removed_items"]

        if removed_items:
            logger.warning(f"Items removed/adjusted during checkout: {removed_items}")

        if not valid_items:
            return Response({"error": "No available products in your cart"}, status=400)

        total = 0
        line_items = []

        for v_item in valid_items:
            product = v_item["product"]
            qty = v_item["quantity"]
            price_inr = v_item["price_inr"]

            total += price_inr * qty
            line_items.append({
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": product.title
                    },
                    "unit_amount": price_inr * 100, # In Cents
                },
                "quantity": qty,
            })

        if total < 50:
            return Response({"error": "Cart total must be at least ₹50"}, status=400)

        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url="https://aikart-shop.onrender.com/success",
            cancel_url="https://aikart-shop.onrender.com/cart",
            metadata={
                "user_id": str(request.user.id)
            }
        )

        # Save Snapshot (Save normalized_items for webhook safety)
        from ..models import CartSnapshot
        CartSnapshot.objects.create(
            stripe_session_id=session.id,
            items=normalized_items
        )

        ActivityLog.objects.create(user=request.user, action="Created checkout session")
        logger.info(f"Checkout Session Created: {session.id} for user_id={request.user.id}")

        response_data = {"url": session.url}
        if removed_items:
            response_data["message"] = "Some items were updated or removed before checkout"

        return Response(response_data)

    except Exception as e:
        logger.error(f"STRIPE CHECKOUT ERROR: {str(e)}")
        return Response({"error": f"Checkout Failed: {str(e)}"}, status=500)




# ==================================================
# STRIPE WEBHOOK
# ==================================================

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        logger.error({
            "event": "invalid_webhook_signature"
        })
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id")
        user_id = session.get("metadata", {}).get("user_id")

        logger.info(f"Webhook Received: {event['type']} for session_id={session_id}")

        if user_id:
            from django.db import transaction
            from django.utils import timezone
            from ..models import CartSnapshot, Order, Product
            from ..utils import validate_cart

            # Idempotency Check
            existing_order = Order.objects.filter(stripe_session_id=session_id).first()
            if existing_order:
                logger.info(f"Order already exists for session_id={session_id}, skipping.")
                return HttpResponse(status=200)

            # Fetch snapshot
            snapshot = CartSnapshot.objects.filter(stripe_session_id=session_id).first()
            if not snapshot:
                logger.error(f"CartSnapshot missing for session_id={session_id}")
                return HttpResponse(status=400)

            try:
                with transaction.atomic():
                    validated = validate_cart(snapshot.items, lock=True)
                    valid_items = validated["valid_items"]
                    removed_items = validated["removed_items"]

                    if removed_items:
                        logger.warning(f"Webhook: items removed/adjusted for session {session_id}: {removed_items}")

                    if not valid_items:
                        logger.error(f"Webhook: No valid items for session {session_id}")
                        return HttpResponse(status=400)

                    total = 0
                    items_snapshot = []

                    for v_item in valid_items:
                        product = v_item["product"]
                        qty = v_item["quantity"]
                        price_inr = v_item["price_inr"]

                        # Deduct Stock
                        product.stock -= qty
                        product.save()

                        total += price_inr * qty
                        items_snapshot.append({
                            "product_id": product.id,
                            "title": product.title,
                            "price": price_inr,
                            "quantity": qty
                        })

                    from django.core.cache import cache
                    for item in valid_items:
                        product = item["product"]
                        cache.delete(f"product_{product.id}")

                    order = Order.objects.create(
                        stripe_session_id=session_id,
                        user_id=user_id,
                        total=total,
                        payment_status="paid",
                        payment_method="stripe",
                        paid_at=timezone.now(),
                        items=items_snapshot
                    )

                    ActivityLog.objects.create(
                        user_id=user_id, 
                        action=f"Payment Success - Order #{order.id}"
                    )

                    # Cleanup Snapshot
                    snapshot.delete()
                    logger.info(f"Order Created Successfully: #{order.id} for session_id={session_id}")

            except Exception as e:
                logger.error({
                    "event": "webhook_failed",
                    "session_id": session_id,
                    "error": str(e)
                })
                return HttpResponse(status=500)

    return HttpResponse(status=200)


