from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Profile


# ==================================================
# UPDATE PROFILE
# ==================================================

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

    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": profile.avatar,
            "theme": profile.theme,
        }
    )
