from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Order
import json
import jwt
import stripe
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

# ✅ USE DJANGO SECRET KEY
JWT_SECRET = settings.SECRET_KEY


# =========================
# ✅ SIGNUP (AUTO LOGIN FIX)
# =========================
@csrf_exempt
def signup(request):
    if request.method != "POST":
        return JsonResponse(
            {"message": "Signup endpoint is live. Use POST."},
            status=200
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return JsonResponse(
            {"error": "All fields are required"},
            status=400
        )

    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {"error": "User already exists"},
            status=400
        )

    try:
        user = User.objects.create(
            name=name,
            email=email,
            password=password
        )
    except Exception as e:
        # 👇 THIS prevents 500 crashes
        return JsonResponse(
            {"error": "Signup failed", "details": str(e)},
            status=400
        )

    return JsonResponse(
        {"message": "Signup successful"},
        status=201
    )


# ==========
# ✅ LOGIN
# ==========
@csrf_exempt
def login(request):

    if request.method == "GET":
        return JsonResponse({
            "message": "Login endpoint is live. Use POST."
        })

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        user = User.objects.get(
            email=data.get("email"),
            password=data.get("password")
        )

        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.utcnow() + timedelta(hours=5)
            },
            JWT_SECRET,
            algorithm="HS256"
        )

        return JsonResponse({
            "token": token,
            "name": user.name,
            "user_id": user.id
        })

    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials"}, status=401)


# =================
# ✅ SAVE ORDER
# =================
@csrf_exempt
def save_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    auth = request.headers.get("Authorization")
    if not auth:
        return JsonResponse({"error": "Token missing"}, status=401)

    try:
        token = auth.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return JsonResponse({"error": "Invalid token"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    Order.objects.create(
        user_id=payload["user_id"],
        items=data.get("items"),
        total=data.get("total")
    )

    return JsonResponse({"message": "Order saved"})


# =================
# ✅ USER ORDERS
# =================
@csrf_exempt
def orders(request):
    auth = request.headers.get("Authorization")
    if not auth:
        return JsonResponse({"error": "Token missing"}, status=401)

    try:
        token = auth.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return JsonResponse({"error": "Invalid token"}, status=401)

    data = list(
        Order.objects.filter(user_id=payload["user_id"]).values()
    )
    return JsonResponse(data, safe=False)


# =====================
# ✅ ADMIN ONLY ORDERS
# =====================
@staff_member_required
def admin_orders(request):
    data = list(Order.objects.all().values())
    return JsonResponse(data, safe=False)


# ==========
# ✅ HEALTH
# ==========
def health(request):
    return JsonResponse({"status": "Backend is healthy ✅"})

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def create_checkout_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    auth = request.headers.get("Authorization")
    if not auth:
        return JsonResponse({"error": "Token missing"}, status=401)

    try:
        token = auth.split(" ")[1]
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return JsonResponse({"error": "Invalid token"}, status=401)

    try:
        data = json.loads(request.body)
        total = int(data.get("total") * 100)  # cents
    except:
        return JsonResponse({"error": "Invalid data"}, status=400)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "inr",
                "product_data": {
                    "name": "ShopKart Order",
                },
                "unit_amount": total,
            },
            "quantity": 1,
        }],
        success_url="https://rrr-shopkart-frontend.onrender.com/success",
        cancel_url="https://rrr-shopkart-frontend.onrender.com/cart",
    )

    return JsonResponse({"url": session.url})
