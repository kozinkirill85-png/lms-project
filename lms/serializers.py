from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import YouTubeURLValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""
    # Автоматически подставляем текущего пользователя при создании
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'course', 'owner']
        validators = [YouTubeURLValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""
    # Автоматически подставляем текущего пользователя при создании
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    lessons_count = serializers.SerializerMethodField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'owner', 'lessons_count', 'lessons', 'is_subscribed']

    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе"""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, course=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки"""

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'course', 'created_at']
        read_only_fields = ['user', 'created_at']