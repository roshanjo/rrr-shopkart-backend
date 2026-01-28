import os
import io
import stripe

from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import Order, Address, Profile


# ================== STRIPE CONFIG ==================
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


# ================== HOME ==================
def home(request):
    return HttpResponse("RRR Shopkart Backend is running 🚀")


# ================== AUTH ==================
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


# ================== ME ==================
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


# ================== UPDATE PROFILE ==================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if "username" in request.data:
        if User.objects.filter(username=request.data["username"]).exclude(id=user.id).exists():
            return Response({"error": "Username already taken"}, status=400)
        user.username = request.data["username"]

    if "password" in request.data:
        user.set_password(request.data["password"])

    if "avatar" in request.data:
        profile.avatar = request.data["avatar"]

    if "theme" in request.data:
        profile.theme = request.data["theme"]

    user.save()
    profile.save()

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": profile.avatar,
        "theme": profile.theme
    })


# ================== STRIPE CHECKOUT ==================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    try:
        total = int(request.data.get("total", 0))

        # 🔐 Stripe minimum (₹50 ≈ $0.60)
        if total < 50:
            return Response(
                {"error": "Cart total must be at least ₹50"},
                status=400
            )

        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": "RRR Shopkart Purchase"
                        },
                        "unit_amount": total * 100,
                    },
                    "quantity": 1
                }
            ],
            success_url="https://aikart-shop.onrender.com/success",
            cancel_url="https://aikart-shop.onrender.com/cart",
            metadata={
                "user_id": str(request.user.id)
            }
        )

        return Response({"url": session.url})

    except Exception as e:
        print("STRIPE CHECKOUT ERROR:", str(e))
        return Response(
            {"error": "Failed to create checkout session"},
            status=500
        )



# ================== STRIPE WEBHOOK ==================
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
                items=[]
            )

    return HttpResponse(status=200)


# ================== ORDERS ==================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return Response([
        {
            "id": o.id,
            "total": o.total,
            "created_at": o.created_at,
            "stripe_session_id": o.stripe_session_id,
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
        "stripe_session_id": order.stripe_session_id,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_invoice(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.drawString(50, 800, "RRR Shopkart - Invoice")
    pdf.drawString(50, 770, f"Order ID: {order.id}")
    pdf.drawString(50, 750, f"Customer: {order.user.username}")
    pdf.drawString(50, 730, f"Email: {order.user.email}")
    pdf.drawString(50, 710, f"Total Paid: ₹{order.total}")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"invoice_{order.id}.pdf"
    )


# ================== ADDRESS ==================
@csrf_exempt
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def address_view(request):
    if request.method == "GET":
        try:
            address = Address.objects.get(user=request.user)
            return Response({
                "id": address.id,
                "full_name": address.full_name,
                "phone": address.phone,
                "street": address.street,
                "city": address.city,
                "state": address.state,
                "pincode": address.pincode,
            })
        except Address.DoesNotExist:
            return Response({}, status=200)

    data = request.data

    required = ["full_name", "phone", "street", "city", "state", "pincode"]
    if not all(data.get(f) for f in required):
        return Response({"error": "All address fields are required"}, status=400)

    address, created = Address.objects.update_or_create(
        user=request.user,
        defaults={
            "full_name": data["full_name"],
            "phone": data["phone"],
            "street": data["street"],
            "city": data["city"],
            "state": data["state"],
            "pincode": data["pincode"],
        }
    )

    return Response({"id": address.id, "created": created}, status=201)
