from django.urls import path
from .views import signup, login, save_order, orders, admin_orders

urlpatterns = [
    path("signup/", signup),
    path("login/", login),
    path("save-order/", save_order),
    path("orders/", orders),
    path("admin/orders/", admin_orders),
]
