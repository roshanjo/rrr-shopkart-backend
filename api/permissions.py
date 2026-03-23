from rest_framework.permissions import BasePermission

class IsCustomAdmin(BasePermission):
    """
    Allows access only to the explicit Admin email.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.email == "admin@aikart.com" and
            getattr(request.user, "username", None) == "admin"
        )
