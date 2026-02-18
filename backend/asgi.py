# Import built-in os module
import os

# Import Django's ASGI application function
from django.core.asgi import get_asgi_application


# --------------------------------------------------
# Set the default Django settings module
# --------------------------------------------------

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "backend.settings"
)


# --------------------------------------------------
# Create the ASGI application
# --------------------------------------------------

application = get_asgi_application()