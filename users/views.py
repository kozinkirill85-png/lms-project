from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, User
from .serializers import PaymentSerializer, UserProfileSerializer

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра платежей с фильтрацией и сортировкой"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для профиля пользователя"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer