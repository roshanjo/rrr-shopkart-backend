from django.urls import path
from .views import signup, login, save_order, orders, admin_orders , health

urlpatterns = [
    path("signup/", signup),
    path("login/", login),
    path("save-order/", save_order),
    path("orders/", orders),
    path("admin/orders/", admin_orders),
    path('health/', health, name='health'),
    path("create-checkout-session/", views.create_checkout_session),
]
