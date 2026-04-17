from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlparse


def validate_youtube_url(value):
    """Проверяет, что ссылка ведет на YouTube"""
    if not value:
        return

    # Защита от передачи нестроковых данных
    if not isinstance(value, str):
        raise ValidationError(_('Некорректный URL адрес'))

    try:
        parsed_url = urlparse(value)
        domain = parsed_url.netloc.lower()

        allowed_domains = [
            'youtube.com', 'www.youtube.com', 'm.youtube.com',
            'youtu.be', 'www.youtu.be',
        ]

        # Точное совпадение
        if domain in allowed_domains:
            return

        # Поддомены (например, music.youtube.com)
        if domain.endswith('.youtube.com') or domain.endswith('.youtu.be'):
            return

        raise ValidationError(
            _('Разрешены только ссылки на YouTube. Получена ссылка: %(domain)s'),
            params={'domain': domain},
        )
    except ValidationError:
        raise
    except Exception:
        raise ValidationError(_('Некорректный URL адрес'))


class YouTubeURLValidator:
    """
    Валидатор уровня сериализатора (для Meta.validators).
    DRF передает сюда словарь всех полей (attrs), а не одно значение.
    """

    def __init__(self, field='video_url'):
        self.field = field

    def __call__(self, attrs):
        # Извлекаем значение нужного поля из словаря данных
        value = attrs.get(self.field)
        validate_youtube_url(value)