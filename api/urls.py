from django.urls import path
from .views import (
    home,
    signup,
    login,
    create_checkout_session,
    stripe_webhook,
)

urlpatterns = [
    path("", home),
    path("signup/", signup),
    path("login/", login),
    path("create-checkout-session/", create_checkout_session),

    # ✅ NEW WEBHOOK ENDPOINT
    path("stripe/webhook/", stripe_webhook),
]
