from django.urls import path
from .views import (
    home,
    create_checkout_session,
    signup,
    login,
)

urlpatterns = [
    path("", home),
    path("signup/", signup),
    path("login/", login),
    path("create-checkout-session/", create_checkout_session),
]
