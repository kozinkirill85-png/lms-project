import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Удаляем старого суперпользователя если есть
User.objects.filter(email='admin@lms.local').delete()

# Создаём нового (НЕ указываем username явно!)
user = User.objects.create_superuser(
    email='admin@lms.local',
    password='Admin123456!',
    # username НЕ передаём - он сгенерируется из email
)

print(f"✅ Суперпользователь {user.email} создан успешно!")
print(f"Username: {user.username}")
print(f"Пароль: Admin123456!")