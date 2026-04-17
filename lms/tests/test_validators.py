from django.test import TestCase
from django.core.exceptions import ValidationError
from lms.validators import validate_youtube_url, YouTubeURLValidator


class YouTubeURLValidatorTestCase(TestCase):
    """Тесты для валидатора YouTube URL"""

    def test_valid_youtube_url(self):
        """Тест валидной ссылки на YouTube"""
        valid_urls = [
            'https://www.youtube.com/watch?v=test123',
            'https://youtube.com/watch?v=test123',
            'https://www.youtube.com/embed/test123',
        ]

        for url in valid_urls:
            try:
                validate_youtube_url(url)
            except ValidationError:
                self.fail(f"Валидный URL {url} вызвал ValidationError")

    def test_invalid_youtube_url(self):
        """Тест невалидной ссылки (не YouTube)"""
        invalid_urls = [
            'https://www.vimeo.com/test123',
            'https://www.example.com/video',
            'https://rutube.ru/video/test',
        ]

        for url in invalid_urls:
            with self.assertRaises(ValidationError):
                validate_youtube_url(url)

    def test_class_validator(self):
        """Тест класс-валидатора"""
        validator = YouTubeURLValidator(field='video_url')

        # Валидный URL
        try:
            validator('https://www.youtube.com/watch?v=test')
        except ValidationError:
            self.fail("Class validator failed on valid URL")

        # Невалидный URL
        with self.assertRaises(ValidationError):
            validator('https://www.vimeo.com/test')