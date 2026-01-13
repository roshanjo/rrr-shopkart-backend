from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from api.views import stripe_webhook

def home(request):
    return HttpResponse("RRR Shopkart Backend is running 🚀")

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),   # ✅ ADD THIS
    path("api/", include("api.urls")),
    path("api/stripe/webhook/", stripe_webhook),
]