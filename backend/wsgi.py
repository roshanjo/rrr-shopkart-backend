"""
WSGI config for backend project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

application = get_wsgi_application()

# ✅ AUTO MIGRATE ON RENDER (FREE PLAN SAFE)
try:
    from django.core.management import call_command
    call_command("migrate", interactive=False)
except Exception as e:
    print("Migration skipped:", e)