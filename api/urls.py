from django.urls import path
from .views import signup, login, save_order, orders

urlpatterns = [
    path("signup/", signup),
    path("login/", login),
    path("order/", save_order),
    path("orders/", orders),
]
