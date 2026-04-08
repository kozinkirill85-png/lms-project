from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User


class Course(models.Model):
    """Модель курса"""
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
        User,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name=_('Владелец'),
        help_text=_('Создатель курса')
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
        User,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('Владелец'),
        help_text=_('Создатель урока')
    )

    class Meta:
        verbose_name = _('Урок')
        verbose_name_plural = _('Уроки')
        ordering = ['id']

    def __str__(self):
        return self.title