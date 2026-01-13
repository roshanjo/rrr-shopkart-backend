from django.urls import path
from .views import (
    home,
    signup,
    login_user,
    me,
    create_checkout_session,
    stripe_webhook,
    my_orders,
    order_detail,
)

urlpatterns = [
    path("", home),

    # AUTH
    path("signup/", signup),
    path("login/", login_user),
    path("me/", me),

    # STRIPE
    path("create-checkout-session/", create_checkout_session),
    path("stripe/webhook/", stripe_webhook),

    # ORDERS
    path("orders/", my_orders),
    path("orders/<int:order_id>/", order_detail),
]
