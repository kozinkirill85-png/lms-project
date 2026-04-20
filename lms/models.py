from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Владелец'),
        help_text=_('Создатель курса'),
        related_name='courses'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Цена'),
        help_text=_('Цена курса в рублях')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
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
        help_text=_('Ссылка на YouTube видео')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_('Курс'),
        related_name='lessons'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Владелец'),
        related_name='lessons'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
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


class Payment(models.Model):
    """Модель платежа"""
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Банковская карта'),
        ('transfer', 'Банковский перевод'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('failed', 'Не удался'),
        ('refunded', 'Возвращен'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='payments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_('Курс'),
        null=True,
        blank=True,
        related_name='payments'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name=_('Урок'),
        null=True,
        blank=True,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Сумма'),
        help_text=_('Сумма платежа в рублях')
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='card',
        verbose_name=_('Способ оплаты')
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name=_('Статус')
    )

    # Stripe поля
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('ID продукта в Stripe')
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('ID цены в Stripe')
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('ID сессии в Stripe')
    )
    stripe_payment_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Ссылка на оплату Stripe')
    )
    stripe_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Статус в Stripe')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Платежи')
        ordering = ['-created_at']

    def __str__(self):
        return f"Платеж #{self.id} - {self.user.email} - {self.amount} руб."