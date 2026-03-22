from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Profile


# ==================================================
# AUTH - SIGNUP
# ==================================================

@api_view(["POST"])
def signup(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response({"error": "All fields are required"}, status=400)

    # Email Validation
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return Response({"error": "Invalid email format"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)

    Profile.objects.create(
        user=user,
        avatar="/avatars/a1.png",
        theme="light"
    )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "token": str(refresh.access_token),
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.profile.avatar,
        },
        status=201
    )


# ==================================================
# AUTH - LOGIN
# ==================================================

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

    return Response(
        {
            "token": str(refresh.access_token),
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": profile.avatar,
        }
    )


# ==================================================
# ME
# ==================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return Response(
        {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "avatar": profile.avatar,
            "theme": profile.theme,
        }
    )
