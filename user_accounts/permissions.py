from rest_framework.permissions import BasePermission

from common.constants import UserRole


class IsAdminUser(BasePermission):
    """
    Custom permission to only allow users with 'admin' role to access.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and has 'admin' role
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN.value
