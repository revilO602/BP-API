from rest_framework import permissions


class CanChangeDeliveryState(permissions.BasePermission):
    """
    Handles permissions for changing delivery state. Only assigned
    courier can change it.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.courier or request.user.is_admin:
            if obj.state == 'ready' or request.user == obj.courier:
                return True
        return False
