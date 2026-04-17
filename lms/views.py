from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Subscription
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    SubscriptionSerializer
)
from .permissions import IsModerator, IsOwner
from .paginators import CoursePagination, LessonPagination


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления курсами.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    def get_permissions(self):
        """
        Назначает права доступа в зависимости от действия.
        """
        if self.action == 'create':
            # Создание: Только обычные пользователи (модераторы не создают)
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            # Удаление: Только владелец (модераторы не удаляют)
            permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['update', 'partial_update']:
            # Редактирование: Модератор ИЛИ Владелец
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            # Просмотр (list, retrieve): Все авторизованные
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Модераторы видят все курсы.
        Обычные пользователи видят только свои курсы.
        """
        user = self.request.user
        if self.action in ['list', 'retrieve']:
            if user.groups.filter(name='Модераторы').exists():
                return Course.objects.all()
            return Course.objects.all()  # ✅ Все авторизованные могут смотреть

            # Для create/update/delete - фильтруем по владельцу
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        Автоматически привязывает создаваемый курс к текущему пользователю.
        """
        serializer.save(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления уроками.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPagination

    def get_permissions(self):
        """
        Назначает права доступа в зависимости от действия.
        """
        if self.action == 'create':
            # Создание: Только обычные пользователи
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            # Удаление: Только владелец
            permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['update', 'partial_update']:
            # Редактирование: Модератор ИЛИ Владелец
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            # Просмотр
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Модераторы видят все уроки.
        Обычные пользователи видят только свои уроки.
        """
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        Автоматически привязывает создаваемый урок к текущему пользователю.
        """
        serializer.save(owner=self.request.user)


class SubscriptionView(APIView):
    """
    Контроллер для подписки/отписки на курс.
    Доступен только авторизованным пользователям.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Логика подписки:
        - Если подписка есть -> удаляем (отписка).
        - Если подписки нет -> создаем (подписка).
        """
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {'error': 'Необходимо передать ID курса (course_id)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем курс или возвращаем 404, если его нет
        course = get_object_or_404(Course, id=course_id)

        # Ищем существующую подписку
        subscription = Subscription.objects.filter(user=user, course=course).first()

        if subscription:
            # Если подписка есть - удаляем её
            subscription.delete()
            message = 'Вы успешно отписались от курса.'
        else:
            # Если подписки нет - создаем её
            Subscription.objects.create(user=user, course=course)
            message = 'Вы успешно подписались на обновления курса.'

        return Response({'message': message}, status=status.HTTP_200_OK)


class SubscriptionListView(generics.ListAPIView):
    """
    Список подписок текущего пользователя.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)