from rest_framework import permissions
from helpers.functions import is_courier


class CanChangeDeliveryState(permissions.BasePermission):
    """
    Handles permissions for changing delivery state. Only assigned
    courier can change it.
    """

    def has_object_permission(self, request, view, obj):
        if is_courier(request.user) or request.user.is_admin:
            if obj.state == 'ready' or request.user == obj.courier.user:
                return True
        return False
