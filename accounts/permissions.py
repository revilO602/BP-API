from rest_framework import permissions


class IsRegistering(permissions.BasePermission):
    """
    Permission checking if user is sending a POST request.
    """
    def has_permission(self, request, view):
        return request.method == "POST"
