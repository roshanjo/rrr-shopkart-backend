from django.urls import path
from .views import health, signup, login

urlpatterns = [
    path("health/", health),
    path("signup/", signup),
    path("login/", login),
]
