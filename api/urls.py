from django.urls import path
from .views import (
    signup,
    login,
    test_api,
    home,
    create_checkout_session,
)

urlpatterns = [
    path("", home),
    path("signup/", signup),
    path("login/", login),
    path("test/", test_api),
    path("create-checkout-session/", create_checkout_session),
]
