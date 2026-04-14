from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """Кастомная модель пользователя"""
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        null=False
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон')
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Город')
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар')
    )

    # Убираем username из обязательных полей, если используете email для входа
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username всё ещё нужен для Django admin

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.email or self.username


class Payment(models.Model):
    """Модель платежа"""

    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Наличные')),
        ('transfer', _('Перевод на счёт')),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='payments'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата оплаты')
    )
    course = models.ForeignKey(
        'lms.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Оплаченный курс'),
        related_name='payments'
    )
    lesson = models.ForeignKey(
        'lms.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Оплаченный урок'),
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Сумма оплаты')
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='transfer',
        verbose_name=_('Способ оплаты')
    )

    class Meta:
        verbose_name = _('Платёж')
        verbose_name_plural = _('Платежи')
        ordering = ['-payment_date']

    def __str__(self):
        if self.course:
            return f"Платёж за курс '{self.course.title}' от {self.user.email}"
        elif self.lesson:
            return f"Платёж за урок '{self.lesson.title}' от {self.user.email}"
        return f"Платёж от {self.user.email}"

    def clean(self):
        """Валидация: должен быть оплачен либо курс, либо урок, но не оба сразу"""
        if self.course and self.lesson:
            raise ValidationError(_('Нельзя оплатить одновременно курс и урок'))
        if not self.course and not self.lesson:
            raise ValidationError(_('Должен быть оплачен либо курс, либо урок'))
