import os
import stripe
import io
import json

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
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": profile.avatar,
        "theme": profile.theme
    })

# ------------------ UPDATE PROFILE ------------------
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    username = request.data.get("username")
    avatar = request.data.get("avatar")
    theme = request.data.get("theme")
    password = request.data.get("password")

    if username:
        user.username = username

    if password:
        user.set_password(password)  # 🔥 THIS WAS MISSING

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

# ------------------ STRIPE WEBHOOK ------------------
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]

        Order.objects.create(
            user_id=user_id,
            total=session["amount_total"] // 100,
            stripe_session_id=session["id"],
            items=[]
        )

    return HttpResponse(status=200)

# ------------------ ORDERS ------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return Response([
        {
            "id": o.id,
            "total": o.total,
            "created_at": o.created_at,
            "stripe_session_id": o.stripe_session_id
        }
        for o in orders
    ])

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return Response({
        "id": order.id,
        "total": order.total,
        "items": order.items,
        "created_at": order.created_at,
        "stripe_session_id": order.stripe_session_id
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_invoice(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.drawString(50, 800, "RRR Shopkart - Invoice")
    pdf.drawString(50, 760, f"Order ID: {order.id}")
    pdf.drawString(50, 740, f"Customer: {order.user.username}")
    pdf.drawString(50, 720, f"Email: {order.user.email}")
    pdf.drawString(50, 700, f"Total Paid: ₹{order.total}")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f"invoice_{order.id}.pdf")

# ------------------ ADDRESS ------------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def address_view(request):
    user = request.user

    # GET: return saved address (single)
    if request.method == "GET":
        address = Address.objects.filter(user=user).first()
        if not address:
            return Response({}, status=200)

        return Response({
            "full_name": getattr(address, "full_name", ""),
            "phone": getattr(address, "phone", ""),
            "address": getattr(address, "address", address.line1 if hasattr(address, "line1") else ""),
            "city": address.city,
            "state": address.state,
            "pincode": address.pincode,
        })

    # POST: create or update
    data = request.data
    address, _ = Address.objects.get_or_create(user=user)

    # Map frontend → backend safely
    address.line1 = data.get("address") or data.get("line1") or ""
    address.city = data.get("city", "")
    address.state = data.get("state", "")
    address.pincode = data.get("pincode", "")

    # Optional fields (only if model has them)
    if hasattr(address, "full_name"):
        address.full_name = data.get("full_name", "")
    if hasattr(address, "phone"):
        address.phone = data.get("phone", "")

    address.save()

    return Response({"message": "Address saved successfully"}, status=200)
