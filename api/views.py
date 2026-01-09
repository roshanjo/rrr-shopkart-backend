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


# --------------------------------------------------
# HOME (KEEP)
# --------------------------------------------------
def home(request):
    return HttpResponse("RRR Shopkart Backend is running 🚀")


# --------------------------------------------------
# AUTH APIs (NEW – SAFE)
# --------------------------------------------------
@api_view(["POST"])
def signup(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response(
            {"error": "All fields are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

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
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.check_password(password):
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "token": str(refresh.access_token),
            "name": user.username,
        },
        status=status.HTTP_200_OK,
    )


# --------------------------------------------------
# STRIPE CHECKOUT (KEEP)
# --------------------------------------------------
@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        data = json.loads(request.body)
        total = int(data.get("total", 0))

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": "Ai-Kart Purchase",
                            },
                            "unit_amount": total * 100,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="https://rrr-shopkart-frontend.onrender.com/success",
                cancel_url="https://rrr-shopkart-frontend.onrender.com/cancel",
            )

            return JsonResponse({"url": session.url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
