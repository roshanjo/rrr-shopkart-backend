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

from .models import Order, Address

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

    user = User.objects.create_user(username=username, email=email, password=password)
    refresh = RefreshToken.for_user(user)

    return Response({
        "token": str(refresh.access_token),
        "id": user.id,
        "username": user.username,
        "email": user.email
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

    refresh = RefreshToken.for_user(user)

    return Response({
        "token": str(refresh.access_token),
        "id": user.id,
        "username": user.username,
        "email": user.email
    }, status=200)

# ------------------ JWT PROTECTED ------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })

# ------------------ ORDERS ------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return Response([
        {"id": o.id, "total": o.total, "created_at": o.created_at, "stripe_session_id": o.stripe_session_id}
        for o in orders
    ])

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

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
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, 800, "RRR Shopkart - Invoice")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 760, f"Order ID: {order.id}")
    pdf.drawString(50, 740, f"Customer: {order.user.username}")
    pdf.drawString(50, 720, f"Email: {order.user.email}")
    pdf.drawString(50, 700, f"Date: {order.created_at.strftime('%d %b %Y %H:%M')}")
    pdf.drawString(50, 660, f"Total Paid: ₹{order.total}")
    pdf.drawString(50, 640, "Payment Status: PAID (Stripe Test Mode)")
    pdf.drawString(50, 600, "Thank you for shopping with RRR Shopkart ❤️")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f"invoice_order_{order.id}.pdf")

# ------------------ STRIPE ------------------
@csrf_exempt
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
        metadata={"user_id": str(request.user.id), "total": str(total)}
    )

    return Response({"url": session.url})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        print("Webhook error:", e)
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        total = metadata.get("total")
        stripe_session_id = session.get("id")
        if user_id and total and not Order.objects.filter(stripe_session_id=stripe_session_id).exists():
            try:
                user = User.objects.get(id=user_id)
                Order.objects.create(
                    user=user,
                    total=int(total),
                    stripe_session_id=stripe_session_id,
                    items={"stripe_session_id": stripe_session_id}
                )
                print("✅ Order saved:", stripe_session_id)
            except User.DoesNotExist:
                pass

    return HttpResponse(status=200)

# ------------------ ADDRESS ------------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def address_view(request):
    user = request.user

    # GET saved address
    if request.method == "GET":
        address = Address.objects.filter(user=user).first()
        if not address:
            return Response(None)
        return Response({
            "fullName": address.full_name,
            "phone": address.phone,
            "street": address.street,
            "city": address.city,
            "state": address.state,
            "pincode": address.pincode
        })

    # POST: create/update address
    if request.method == "POST":
        data = request.data
        address, created = Address.objects.update_or_create(
            user=user,
            defaults={
                "full_name": data.get("fullName", ""),
                "phone": data.get("phone", ""),
                "street": data.get("street", ""),
                "city": data.get("city", ""),
                "state": data.get("state", ""),
                "pincode": data.get("pincode", "")
            }
        )
        return Response({"id": address.id})
