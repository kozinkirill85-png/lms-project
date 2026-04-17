from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Course(models.Model):
    """Модель курса"""
    objects = None
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название'),
        help_text=_('Введите название курса')
    )
    preview = models.ImageField(
        upload_to='courses/previews/',
        blank=True,
        null=True,
        verbose_name=_('Превью'),
        help_text=_('Загрузите изображение для курса')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Описание'),
        help_text=_('Введите описание курса')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Владелец'),
        help_text=_('Создатель курса'),
        related_name='courses'
    )

    class Meta:
        verbose_name = _('Курс')
        verbose_name_plural = _('Курсы')
        ordering = ['title']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока"""
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название'),
        help_text=_('Введите название урока')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Описание'),
        help_text=_('Введите описание урока')
    )
    preview = models.ImageField(
        upload_to='lessons/previews/',
        blank=True,
        null=True,
        verbose_name=_('Превью'),
        help_text=_('Загрузите изображение для урока')
    )
    video_url = models.URLField(
        verbose_name=_('Ссылка на видео'),
        help_text=_('Введите ссылку на видеоурок')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('Курс'),
        help_text=_('Курс, к которому относится урок')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Владелец'),
        help_text=_('Создатель урока'),
        related_name='lessons'
    )

    class Meta:
        verbose_name = _('Урок')
        verbose_name_plural = _('Уроки')
        ordering = ['id']

    def __str__(self):
        return self.title


class Subscription(models.Model):
    """Модель подписки пользователя на курс"""
    objects = None
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='subscriptions'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_('Курс'),
        related_name='subscribers'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата подписки')
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        unique_together = ['user', 'course']  # Пользователь может подписаться на курс только один раз
        ordering = ['-created_at']

    def __str__(self):
        return f"Подписка {self.user.email} на курс {self.course.title}"