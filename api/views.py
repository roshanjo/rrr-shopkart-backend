from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Order
import json
import jwt
from datetime import datetime, timedelta

SECRET = "SECRET123"

@csrf_exempt
def signup(request):
    if request.method == "GET":
        return JsonResponse(
            {"message": "Signup endpoint is live. Use POST to signup."}
        )

    if request.method != "POST":
        return JsonResponse(
            {"error": "Invalid request method"}, status=400
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"}, status=400
        )

    if User.objects.filter(email=data.get("email")).exists():
        return JsonResponse(
            {"error": "User already exists"}, status=400
        )

    User.objects.create(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password"),
    )

    return JsonResponse({"message": "Signup successful"})

@csrf_exempt
def login(request):
    data = json.loads(request.body)

    try:
        user = User.objects.get(
            email=data["email"],
            password=data["password"]
        )
        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.utcnow() + timedelta(hours=5)
            },
            SECRET,
            algorithm="HS256"
        )

        return JsonResponse({
            "token": token,
            "name": user.name,
            "user_id": user.id
        })
    except:
        return JsonResponse({"error": "Invalid credentials"}, status=401)


@csrf_exempt
def save_order(request):
    token = request.headers.get("Authorization").split(" ")[1]
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])

    data = json.loads(request.body)

    Order.objects.create(
        user_id=payload["user_id"],
        items=data["items"],
        total=data["total"]
    )

    return JsonResponse({"message": "Order saved"})


def orders(request):
    user_id = request.GET.get("user")
    data = list(Order.objects.filter(user_id=user_id).values())
    return JsonResponse(data, safe=False)
