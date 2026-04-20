from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Course, Subscription

User = get_user_model()


@shared_task
def send_course_update_notification(course_id, course_title, user_email):
    """
    Отправляет уведомление об обновлении курса
    """
    subject = f'Курс "{course_title}" обновлен!'
    message = f'Здравствуйте!\n\nВ курсе "{course_title}" появились новые материалы.\n\n' \
              f'Перейдите в личный кабинет, чтобы ознакомиться с обновлениями.\n\n' \
              f'С уважением,\nКоманда LMS'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )

    return f'Email sent to {user_email}'


@shared_task
def notify_subscribers_about_course_update(course_id):
    """
    Отправляет уведомления всем подписчикам курса об его обновлении.
    Проверяет, что курс не обновлялся более 4 часов (дополнительное задание).
    """
    try:
        course = Course.objects.select_related('owner').get(id=course_id)

        # Дополнительное задание: проверяем, что курс не обновлялся более 4 часов
        four_hours_ago = timezone.now() - timedelta(hours=4)
        if course.updated_at > four_hours_ago:
            # Курс обновлялся менее 4 часов назад - не отправляем уведомление
            return f'Course {course_id} was updated less than 4 hours ago. Notification skipped.'

        # Получаем всех подписчиков курса
        subscriptions = Subscription.objects.filter(course=course).select_related('user')

        notified_count = 0
        for subscription in subscriptions:
            # Отправляем задачу на отправку email асинхронно
            send_course_update_notification.delay(
                course_id=course.id,
                course_title=course.title,
                user_email=subscription.user.email
            )
            notified_count += 1

        return f'Notifications sent to {notified_count} subscribers for course "{course.title}"'

    except Course.DoesNotExist:
        return f'Course {course_id} does not exist'
    except Exception as e:
        return f'Error sending notifications: {str(e)}'


@shared_task
def deactivate_inactive_users():
    """
    Периодическая задача: блокирует пользователей, которые не заходили более месяца.
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим пользователей, которые не заходили более месяца и активны
    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    ).exclude(
        is_superuser=True  # Не блокируем суперпользователей
    )

    deactivated_count = inactive_users.count()

    # Блокируем пользователей
    inactive_users.update(is_active=False)

    return f'Deactivated {deactivated_count} inactive users'