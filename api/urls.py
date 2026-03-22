from django.urls import path
from .views.home import home
from .views.auth import signup, login_user, me
from .views.profile import update_profile
from .views.payments import create_checkout_session, stripe_webhook
from .views.orders import my_orders, order_detail, order_invoice
from .views.address import address_view



# ============================
# URL Patterns
# ============================

urlpatterns = [

    # Home
    path(
        "",
        home
    ),

    # Authentication
    path(
        "signup/",
        signup
    ),
    path(
        "login/",
        login_user
    ),
    path(
        "me/",
        me
    ),

    # Profile
    path(
        "profile/",
        update_profile
    ),

    # Stripe Payments
    path(
        "create-checkout-session/",
        create_checkout_session
    ),
    path(
        "stripe/webhook/",
        stripe_webhook
    ),

    # Orders
    path(
        "orders/",
        my_orders
    ),
    path(
        "orders/<int:order_id>/",
        order_detail
    ),
    path(
        "orders/<int:order_id>/invoice/",
        order_invoice
    ),

    # Address
    path(
        "address/",
        address_view
    ),
]