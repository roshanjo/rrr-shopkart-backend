from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "status": "OK",
        "message": "RRR ShopKart Backend is running"
    })

urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]
