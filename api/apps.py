from django.apps import AppConfig


class ApiConfig(AppConfig):

    # Default primary key field type
    default_auto_field = "django.db.models.BigAutoField"

    # App name
    name = "api"