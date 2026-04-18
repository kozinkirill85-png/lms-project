from rest_framework import serializers
from .models import Course, Lesson, Subscription, Payment
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
        fields = ['id', 'title', 'preview', 'description', 'owner', 'price',
                  'lessons_count', 'lessons', 'is_subscribed']

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


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания платежа с интеграцией Stripe"""

    class Meta:
        model = Payment
        fields = ['id', 'user', 'course', 'lesson', 'amount', 'payment_method']
        read_only_fields = ['user', 'stripe_payment_url', 'stripe_status', 'status']

    def create(self, validated_data):
        from .services.stripe_service import StripeService

        # Сохраняем платеж сначала в нашей БД
        payment = super().create(validated_data)

        # Интеграция со Stripe
        try:
            # 1. Создаем продукт
            product_name = f"Оплата: {payment.course.title if payment.course else payment.lesson.title}"
            product_description = f"Платеж пользователя {payment.user.email}"

            product = StripeService.create_product(
                name=product_name,
                description=product_description
            )
            payment.stripe_product_id = product['id']

            # 2. Создаем цену (amount в копейках!)
            amount_in_cents = int(payment.amount * 100)
            price = StripeService.create_price(
                product_id=product['id'],
                amount=amount_in_cents
            )
            payment.stripe_price_id = price['id']

            # 3. Создаем сессию оплаты
            session = StripeService.create_checkout_session(
                price_id=price['id'],
                success_url='http://localhost:8000/payment/success/',
                cancel_url='http://localhost:8000/payment/cancel/',
                user_email=payment.user.email
            )
            payment.stripe_session_id = session['id']
            payment.stripe_payment_url = session['url']
            payment.stripe_status = session['status']

            payment.save()

        except Exception as e:
            # Если ошибка со Stripe - удаляем платеж из нашей БД
            payment.delete()
            raise serializers.ValidationError(f'Ошибка при создании платежа: {str(e)}')

        return payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра платежа"""

    class Meta:
        model = Payment
        fields = ['id', 'user', 'course', 'lesson', 'amount', 'payment_method',
                  'status', 'stripe_payment_url', 'stripe_status', 'created_at']
        read_only_fields = fields


class PaymentStatusSerializer(serializers.Serializer):
    """Сериализатор для проверки статуса платежа"""
    payment_id = serializers.IntegerField(read_only=True)
    stripe_status = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(read_only=True)
    amount_total = serializers.IntegerField(read_only=True)
    currency = serializers.CharField(read_only=True)