import os
import json
import stripe

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


# --------------------------------------------------
# STRIPE CONFIG
# --------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")


# --------------------------------------------------
# HOME
# --------------------------------------------------
def home(request):
    return HttpResponse("Ai-Kart Backend is running 🚀")


# --------------------------------------------------
# AUTH APIs
# --------------------------------------------------
@api_view(["POST"])
def signup(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response({"error": "All fields are required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "token": str(refresh.access_token),
            "name": user.username,
        },
        status=201,
    )


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = User.objects.get(email=email)
        if not user.check_password(password):
            raise User.DoesNotExist
    except User.DoesNotExist:
        return Response({"error": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "token": str(refresh.access_token),
            "name": user.username,
        },
        status=200,
    )


# --------------------------------------------------
# STRIPE CHECKOUT
# --------------------------------------------------
@csrf_exempt
def create_checkout_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)
    total = int(data.get("total", 0))

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {"name": "Ai-Kart Purchase"},
                        "unit_amount": total * 100,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://aikart-shop.onrender.com/success",
            cancel_url="https://aikart-shop.onrender.com/cart",
        )

        return JsonResponse({"url": session.url})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# --------------------------------------------------
# ✅ STRIPE WEBHOOK (NEW & IMPORTANT)
# --------------------------------------------------
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        return HttpResponse(status=400)

    # ✅ PAYMENT CONFIRMED BY STRIPE
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        print("✅ Payment verified:", session["id"])
        print("💰 Amount:", session["amount_total"])

        # (Next step: save order to database)

    return HttpResponse(status=200)
