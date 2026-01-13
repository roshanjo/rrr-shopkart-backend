import os
import json
import stripe

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Order


# --------------------------------------------------
# STRIPE CONFIG (TEST MODE)
# --------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")  # sk_test_...
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")


# --------------------------------------------------
# HOME
# --------------------------------------------------
def home(request):
    return HttpResponse("RRR Shopkart Backend is running 🚀")


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
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
        status=201,
    )


@api_view(["POST"])
def login_user(request):
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
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
        status=200,
    )


# --------------------------------------------------
# JWT PROTECTED
# --------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    )


# --------------------------------------------------
# STRIPE CHECKOUT (FIXED)
# --------------------------------------------------
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    data = request.data
    total = int(data.get("total", 0))

    if total <= 0:
        return Response({"error": "Invalid total"}, status=400)

    user = request.user  # ✅ FIXED (JWT USER)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": "RRR Shopkart Purchase"},
                    "unit_amount": total * 100,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="https://aikart-shop.onrender.com/success",
        cancel_url="https://aikart-shop.onrender.com/cart",
        metadata={
            "user_id": str(user.id),
            "total": str(total),
        },
    )

    return Response({"url": session.url})


# --------------------------------------------------
# STRIPE WEBHOOK (TEST MODE SAFE)
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
    except Exception as e:
        print("❌ Webhook error:", e)
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        total = metadata.get("total")
        stripe_session_id = session.get("id")

        if not user_id or not total:
            return HttpResponse(status=200)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponse(status=200)

        if Order.objects.filter(stripe_session_id=stripe_session_id).exists():
            return HttpResponse(status=200)

        Order.objects.create(
            user=user,
            items={"stripe_session_id": stripe_session_id},
            total=int(total),
            stripe_session_id=stripe_session_id,
        )

        print("✅ Order saved:", stripe_session_id)

    return HttpResponse(status=200)
