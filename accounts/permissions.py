from rest_framework import permissions


class IsRegistering(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method == "POST"
