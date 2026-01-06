from django.http import JsonResponse
import jwt
from django.conf import settings

JWT_SECRET = settings.SECRET_KEY

PUBLIC_PATHS = [
    "/api/login/",
    "/api/signup/",
    "/api/health/",
    "/admin/",
]

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ✅ Allow public routes
        for path in PUBLIC_PATHS:
            if request.path.startswith(path):
                return self.get_response(request)

        auth = request.headers.get("Authorization")
        if not auth:
            return JsonResponse({"error": "Token missing"}, status=401)

        try:
            token = auth.split(" ")[1]
            jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except Exception:
            return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)
