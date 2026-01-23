import os
import stripe
import io

from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import Order, Address, Profile

# ------------------ STRIPE ------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# ------------------ HOME ------------------
def home(request):
    return HttpResponse("RRR Shopkart Backend is running 🚀")

# ------------------ AUTH ------------------
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
        password=password
    )

    Profile.objects.create(
        user=user,
        avatar="/avatars/a1.png",
        theme="light"
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        "token": str(refresh.access_token),
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.profile.avatar
    }, status=201)

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

    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={"avatar": "/avatars/a1.png", "theme": "light"}
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        "token": str(refresh.access_token),
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": profile.avatar
    })

# ------------------ ME ------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "avatar": profile.avatar,
        "theme": profile.theme
    })

# ------------------ UPDATE PROFILE ------------------
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    username = request.data.get("username")
    avatar = request.data.get("avatar")
    theme = request.data.get("theme")
    password = request.data.get("password")

    if username and username != user.username:
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            return Response({"error": "Username already taken"}, status=400)
        user.username = username

    if password:
        user.set_password(password)

    user.save()

    if avatar:
        profile.avatar = avatar

    if theme:
        profile.theme = theme

    profile.save()

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": profile.avatar,
        "theme": profile.theme
    })

# ------------------ STRIPE CHECKOUT ------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    total = int(request.data.get("total", 0))
    if total <= 0:
        return Response({"error": "Invalid total"}, status=400)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "inr",
                "product_data": {"name": "RRR Shopkart Purchase"},
                "unit_amount": total * 100,
            },
            "quantity": 1
        }],
        mode="payment",
        success_url="https://aikart-shop.onrender.com/success",
        cancel_url="https://aikart-shop.onrender.com/cart",
        metadata={"user_id": request.user.id}
    )

    return Response({"url": session.url})

# ------------------ ADDRESS ------------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def address_view(request):
    if request.method == "GET":
        addresses = Address.objects.filter(user=request.user)

        return Response([
            {
                "id": a.id,
                "line1": a.line1,
                "city": a.city,
                "state": a.state,
                "pincode": a.pincode
            }
            for a in addresses
        ], status=200)

    # -------- POST --------
    line1 = request.data.get("line1")
    city = request.data.get("city")
    state = request.data.get("state")
    pincode = request.data.get("pincode")

    if not all([line1, city, state, pincode]):
        return Response(
            {"error": "All address fields are required"},
            status=400
        )

    address = Address.objects.create(
        user=request.user,
        line1=line1,
        city=city,
        state=state,
        pincode=pincode
    )

    return Response({"id": address.id}, status=201)
