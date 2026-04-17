from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonViewSet, SubscriptionView

# Создаем роутер и регистрируем ViewSets
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')

urlpatterns = [
    # Все маршруты для курсов и уроков через роутер
    path('', include(router.urls)),

    # Маршрут для подписки (он не во ViewSet, поэтому прописываем вручную)
    path('subscribe/', SubscriptionView.as_view(), name='subscribe'),
]