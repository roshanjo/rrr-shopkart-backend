import os
import stripe

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Order, Product


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
        items = request.data.get("items", [])  # Expects list of {id, qty}

        if not items:
            return Response({"error": "Cart is empty"}, status=400)

        total = 0
        line_items = []

        # Backend verifies total using local Product DB
        for item in items:
            prod_id = item.get("id")
            qty = int(item.get("qty", 1))

            # Defensive Check
            if qty <= 0:
                return Response({"error": "Invalid quantity"}, status=400)

            try:
                db_item = Product.objects.get(id=prod_id)
                total += db_item.price_inr * qty
                
                line_items.append({
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": db_item.title
                        },
                        "unit_amount": db_item.price_inr * 100, # In Cents
                    },
                    "quantity": qty,
                })
                
            except Product.DoesNotExist:
                return Response({"error": "Invalid product"}, status=400)

        # Confirm minimum order total for Stripe (₹50)
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

        return Response({"url": session.url})

    except Exception as e:
        print("STRIPE CHECKOUT ERROR:", str(e))
        return Response({"error": "Failed to create checkout session"}, status=500)


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
    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")

        if user_id:
            Order.objects.create(
                user_id=user_id,
                total=session["amount_total"] // 100,
                stripe_session_id=session["id"],
                items=[] # Unstructured backup
            )

    return HttpResponse(status=200)
