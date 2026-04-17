from rest_framework import permissions
from .models import Course


class IsModerator(permissions.BasePermission):
    """
    Разрешение только для модераторов
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()


class IsOwner(permissions.BasePermission):
    """
    Разрешение только для владельца объекта
    """

    def has_permission(self, request, view):
        # Для list/create операций проверяем базовую аутентификацию
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Проверяем, что объект имеет поле owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False