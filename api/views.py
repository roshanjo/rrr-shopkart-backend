import json
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


# ---------- BASIC APIs (unchanged) ----------

@csrf_exempt
def signup(request):
    return JsonResponse({"message": "Signup API working"})


@csrf_exempt
def login(request):
    return JsonResponse({"message": "Login API working"})


@csrf_exempt
def test_api(request):
    return JsonResponse({"message": "Backend running successfully 🚀"})


def home(request):
    return HttpResponse("RRR Shopkart Backend is running 🚀")


# ---------- STRIPE CHECKOUT API (NEW) ----------

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def create_checkout_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body)
        total = data.get("total", 0)

        if total <= 0:
            return JsonResponse({"error": "Invalid total"}, status=400)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": "RRR Shopkart Order",
                        },
                        "unit_amount": int(total * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://rrr-shopkart-frontend.onrender.com/success",
            cancel_url="https://rrr-shopkart-frontend.onrender.com/cart",
        )

        return JsonResponse({"url": session.url})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
