from rest_framework import permissions

class IsModerator(permissions.BasePermission):
    """Разрешение только для модераторов"""
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()

class IsOwner(permissions.BasePermission):
    """Разрешение только для владельца объекта"""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user