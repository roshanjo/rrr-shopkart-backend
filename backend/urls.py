# --------------------------------------------------
# IMPORTS
# --------------------------------------------------

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include


# --------------------------------------------------
# SIMPLE HOME VIEW
# --------------------------------------------------

def home(request):
    """
    This function runs when someone visits:
    http://your-domain.com/

    It returns a simple text response.
    """
    return HttpResponse(
        "RRR Shopkart Backend is running 🚀"
    )


# --------------------------------------------------
# URL PATTERNS
# --------------------------------------------------

urlpatterns = [

    # Homepage
    path(
        "",
        home
    ),

    # Django Admin Panel
    path(
        "admin/",
        admin.site.urls
    ),

    # API Routes
    path(
        "api/",
        include("api.urls")
    ),
]