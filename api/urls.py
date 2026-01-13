from django.urls import path
from .views import (home, signup, login_user, me, create_checkout_session, stripe_webhook,)

urlpatterns = [
    path("", home),

    # AUTH
    path("signup/", signup),
    path("login/", login_user),
    path("me/", me),

    # STRIPE
    path("create-checkout-session/", create_checkout_session),
    path("stripe/webhook/", stripe_webhook),

    # WEBHOOK
    path("stripe/webhook/", stripe_webhook)
]
