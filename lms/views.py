from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

# Для документации (drf-spectacular)
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Course, Lesson, Subscription, Payment
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    SubscriptionSerializer,
    PaymentCreateSerializer,
    PaymentSerializer
)
from .permissions import IsModerator, IsOwner
from .paginators import CoursePagination, LessonPagination


@extend_schema(tags=['Courses'])
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
        Обычные пользователи видят все курсы для просмотра, но свои для редактирования.
        """
        user = self.request.user
        # Для list и retrieve показываем все курсы
        if self.action in ['list', 'retrieve']:
            return Course.objects.all()
        # Для create/update/delete фильтруем по владельцу (если не модератор, но проверка есть в permissions)
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        Автоматически привязывает создаваемый курс к текущему пользователю.
        """
        serializer.save(owner=self.request.user)


@extend_schema(tags=['Lessons'])
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


@extend_schema(tags=['Subscriptions'])
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


@extend_schema(tags=['Subscriptions'])
class SubscriptionListView(generics.ListAPIView):
    """
    Список подписок текущего пользователя.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


# ==========================================
# ИНТЕГРАЦИЯ STRIPE (Оплата)
# ==========================================

@extend_schema(tags=['Payments'])
class PaymentCreateView(generics.CreateAPIView):
    """
    Создание платежа с интеграцией Stripe.
    Логика работы со Stripe находится в PaymentCreateSerializer.
    """
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Автоматически привязываем текущего пользователя к платежу
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Переопределяем create, чтобы вернуть удобный ответ
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(user=request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'id': payment.id,
                'amount': payment.amount,
                'payment_url': payment.stripe_payment_url,  # Ссылка на оплату
                'status': payment.stripe_status,
                'message': 'Перейдите по ссылке для оплаты'
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


@extend_schema(tags=['Payments'])
class PaymentStatusView(generics.RetrieveAPIView):
    """
    Проверка статуса платежа (дополнительное задание).
    Позволяет узнать, прошел ли платеж в Stripe.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        from .services.stripe_service import StripeService

        payment = self.get_object()

        if not payment.stripe_session_id:
            return Response(
                {'error': 'Платеж не связан с Stripe'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем актуальный статус из Stripe
        try:
            stripe_data = StripeService.retrieve_session(payment.stripe_session_id)

            # Обновляем статус в нашей БД
            payment.stripe_status = stripe_data['status']
            payment.save()

            return Response({
                'payment_id': payment.id,
                'stripe_status': stripe_data['status'],
                'payment_status': stripe_data.get('payment_status', 'unknown'),
                'amount_total': stripe_data.get('amount_total'),
                'currency': stripe_data.get('currency'),
            })
        except Exception as e:
            return Response(
                {'error': f'Ошибка при получении статуса: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )