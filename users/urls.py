from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'profile', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
