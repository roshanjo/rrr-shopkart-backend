from django.http import JsonResponse

PUBLIC_PATHS = [
    "/api/login/",
    "/api/signup/",
    "/api/health/",
]

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # ✅ Allow Django admin
        if path.startswith("/admin/"):
            return self.get_response(request)

        # ✅ Allow public API routes
        if path in PUBLIC_PATHS:
            return self.get_response(request)

        # 🔐 Protect other API routes
        if path.startswith("/api/"):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return JsonResponse(
                    {"error": "Token missing"},
                    status=401
                )

        return self.get_response(request)
