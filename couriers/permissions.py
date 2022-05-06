from rest_framework import permissions


class IsCourier(permissions.BasePermission):
    """
    Permission checking if user is a courier.
    """
    def has_permission(self, request, view):
        if request.user and request.user.courier:
            return True
        return False
