from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()

    def __call__(self, request):
        # Skip auth for public routes
        public_paths = [
            "/api/login/",
            "/api/signup/",
            "/api/health/",
            "/api/create-checkout-session/",
        ]

        if request.path in public_paths:
            return self.get_response(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"error": "Authorization header missing"},
                status=401
            )

        try:
            auth_result = self.jwt_authenticator.authenticate(request)
            if auth_result is not None:
                request.user, request.auth = auth_result
        except AuthenticationFailed:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401
            )

        return self.get_response(request)
