from django.http import JsonResponse
from django.urls import resolve
from rest_framework_simplejwt.authentication import JWTAuthentication

EXEMPT_URLS = [
    'login',
    'signup',
    'health',
]

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        resolver = resolve(request.path_info)

        # Allow public routes
        if resolver.url_name in EXEMPT_URLS:
            return self.get_response(request)

        # Only protect /api/*
        if request.path.startswith('/api/'):
            header = request.headers.get('Authorization')

            if not header:
                return JsonResponse({"error": "Token missing"}, status=401)

            try:
                token = header.split(' ')[1]
                validated_token = self.jwt_auth.get_validated_token(token)
                request.user = self.jwt_auth.get_user(validated_token)
            except Exception:
                return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)
