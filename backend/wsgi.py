# --------------------------------------------------
# IMPORTS
# --------------------------------------------------

import os
from django.core.wsgi import get_wsgi_application


# --------------------------------------------------
# SET DJANGO SETTINGS MODULE
# --------------------------------------------------

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "backend.settings"
)


# --------------------------------------------------
# CREATE WSGI APPLICATION
# --------------------------------------------------

application = get_wsgi_application()


# --------------------------------------------------
# AUTO MIGRATE ON RENDER (FREE PLAN SAFE)
# --------------------------------------------------
# This will automatically run migrations when the
# project starts (useful for free hosting like Render)

try:
    from django.core.management import call_command

    call_command(
        "migrate",
        interactive=False
    )

except Exception as e:
    print("Migration skipped:", e)