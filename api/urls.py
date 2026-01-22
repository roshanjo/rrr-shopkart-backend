from django.urls import path
from .views import (
    home,
    signup,
    login_user,
    me,
    update_profile,
    create_checkout_session,
    stripe_webhook,
    my_orders,
    order_detail,
    order_invoice,
    address_view,
)

urlpatterns = [
    path("", home),

    path("signup/", signup),
    path("login/", login_user),
    path("me/", me),
    path("profile/", update_profile),

    path("create-checkout-session/", create_checkout_session),
    path("stripe/webhook/", stripe_webhook),

    path("orders/", my_orders),
    path("orders/<int:order_id>/", order_detail),
    path("orders/<int:order_id>/invoice/", order_invoice),

    path("address/", address_view),
]
