from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.models import Course, Lesson
from users.models import Payment
from decimal import Decimal
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает тестовые платежи для пользователей'

    def handle(self, *args, **kwargs):
        # Получаем пользователей
        users = User.objects.all()[:5]  # Первые 5 пользователей

        # Получаем курсы и уроки
        courses = Course.objects.all()[:3]
        lessons = Lesson.objects.all()[:5]

        if not users or (not courses and not lessons):
            self.stdout.write(self.style.ERROR('Нет пользователей, курсов или уроков для создания платежей'))
            return

        # Создаем платежи
        payments_created = 0

        for user in users:
            # Создаем платежи за курсы
            for course in courses:
                Payment.objects.create(
                    user=user,
                    course=course,
                    amount=Decimal(random.uniform(1000, 5000)).quantize(Decimal('0.01')),
                    payment_method=random.choice(['cash', 'transfer']),
                    payment_date=timezone.now() - timedelta(days=random.randint(1, 30))
                )
                payments_created += 1

            # Создаем платежи за уроки
            for lesson in lessons:
                Payment.objects.create(
                    user=user,
                    lesson=lesson,
                    amount=Decimal(random.uniform(200, 1000)).quantize(Decimal('0.01')),
                    payment_method=random.choice(['cash', 'transfer']),
                    payment_date=timezone.now() - timedelta(days=random.randint(1, 30))
                )
                payments_created += 1

        self.stdout.write(self.style.SUCCESS(f'Успешно создано {payments_created} платежей'))
