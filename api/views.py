from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import json

def health(request):
    return JsonResponse({"status": "Backend is alive ✅"})


def signup(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if User.objects.filter(username=email).exists():
        return JsonResponse({"error": "User already exists"}, status=400)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=name
    )

    return JsonResponse({"message": "Signup successful"})


def login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    email = data.get("email")
    password = data.get("password")

    user = authenticate(username=email, password=password)

    if not user:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    return JsonResponse({
        "message": "Login successful",
        "user_id": user.id,
        "name": user.first_name,
    })
