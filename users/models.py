from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя с авторизацией по email"""

    def create_user(self, email, password=None, **extra_fields):
        """Создание и сохранение обычного пользователя"""
        if not email:
            raise ValueError(_('Пользователь должен иметь адрес электронной почты'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание и сохранение суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя"""
    username = None  # Удаляем поле username

    email = models.EmailField(
        unique=True,
        verbose_name=_('Email'),
        help_text=_('Введите вашу электронную почту')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон'),
        help_text=_('Введите ваш номер телефона')
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Город'),
        help_text=_('Введите ваш город')
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар'),
        help_text=_('Загрузите ваш аватар')
    )

    USERNAME_FIELD = 'email'  # Устанавливаем email как поле для авторизации
    REQUIRED_FIELDS = []  # Дополнительные обязательные поля

    objects = UserManager()  # Используем кастомный менеджер

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.email