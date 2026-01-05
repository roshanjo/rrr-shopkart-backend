import jwt
from django.http import JsonResponse
from django.conf import settings

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Only protect these APIs
        if request.path.startswith("/api/") and request.path not in [
            "/api/login/",
            "/api/signup/"
        ]:
            auth = request.headers.get("Authorization")

            if not auth:
                return JsonResponse({"error": "Token missing"}, status=401)

            try:
                token = auth.split(" ")[1]
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"]
                )
                request.user_id = payload["user_id"]
            except:
                return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)
