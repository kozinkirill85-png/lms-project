from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели пользователя с авторизацией по email.
    """
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет обычного пользователя.
        """
        if not email:
            raise ValueError(_('Пользователь должен иметь адрес электронной почты'))

        email = self.normalize_email(email)

        # Генерируем username из email, если он не передан явно
        # Это нужно, так как AbstractUser требует поле username
        username = extra_fields.get('username', email.split('@')[0])

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает и сохраняет суперпользователя.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))

        # Вызываем create_user, который мы написали выше
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя
    """
    email = models.EmailField(_('email address'), unique=True)

    # Указываем, что вход будет по email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # username не требуется при создании

    objects = UserManager()

    def __str__(self):
        return self.email