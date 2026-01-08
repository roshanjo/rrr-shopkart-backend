from django.contrib import admin
from django.urls import path, include
from .views import signup, login, test_api, home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("api.urls")),           
    path("signup/", signup),
    path("login/", login),
    path("test/", test_api),
]
