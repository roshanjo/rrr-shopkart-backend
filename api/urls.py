from django.urls import path
from .views import create_checkout_session, home

urlpatterns = [
    path("", home),
    path("create-checkout-session/", create_checkout_session),
]
