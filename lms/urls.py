from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonViewSet,
    SubscriptionView,
    SubscriptionListView,
    PaymentCreateView,
    PaymentStatusView
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')

urlpatterns = [
    path('', include(router.urls)),
    path('subscribe/', SubscriptionView.as_view(), name='subscribe'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),

    # Маршруты для оплаты
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:pk>/', PaymentStatusView.as_view(), name='payment-status'),
]