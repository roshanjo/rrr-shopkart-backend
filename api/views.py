from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Order
import json
import jwt
from datetime import datetime, timedelta

SECRET = "SECRET123"

@csrf_exempt
def signup(request):
    data = json.loads(request.body)
    User.objects.create(**data)
    return JsonResponse({"message": "Signup success"})


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
