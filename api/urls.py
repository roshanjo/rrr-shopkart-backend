from django.urls import path
from .views import signup, login, test_api, home

urlpatterns = [
    path("", home),            # root /
    path("signup/", signup),
    path("login/", login),
    path("test/", test_api),
]
