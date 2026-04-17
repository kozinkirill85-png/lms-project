from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    """Тесты для CRUD операций с уроками"""

    def setUp(self):
        self.client = APIClient()

        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Создаем модератора
        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            password='modpass123',
            first_name='Mod',
            last_name='User'
        )

        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name='Модераторы')
        self.moderator.groups.add(self.moderator_group)

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Description',
            video_url='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.user
        )

    def test_create_lesson_as_moderator(self):
        """Тест создания урока модератором (должно быть запрещено)"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_url': 'https://www.youtube.com/watch?v=newtest',
            'course': self.course.id
        }
        # ✅ Исправлен URL: роутер DRF использует /lessons/ для POST
        response = self.client.post('/lms/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_as_regular_user(self):
        """Тест создания урока обычным пользователем (должно быть разрешено)"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_url': 'https://www.youtube.com/watch?v=test123',
            'course': self.course.id,
        }

        response = self.client.post('/lms/lessons/', data, format='json')

        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error details: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_invalid_youtube_url(self):
        """Тест создания урока с невалидной ссылкой (не YouTube)"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_url': 'https://www.vimeo.com/watch?v=test',  # Не YouTube
            'course': self.course.id
        }
        response = self.client.post('/lms/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_lesson_as_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Lesson Title'}
        # Используем правильный URL с ID урока
        response = self.client.patch(
            f'/lms/lessons/{self.lesson.id}/',  # ← Обрати внимание на слэш в конце
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson Title')

    def test_delete_lesson_as_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        # ✅ Исправлен URL: роутер DRF использует /lessons/<id>/ для DELETE
        response = self.client.delete(f'/lms/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())


class SubscriptionTestCase(APITestCase):
    """Тесты для подписки на курсы"""

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='subscriber@example.com',
            password='subpass123',
            first_name='Subscriber',
            last_name='User'
        )

        self.course_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123',
            first_name='Owner',
            last_name='User'
        )

        self.course = Course.objects.create(
            title='Test Course for Subscription',
            description='Test Description',
            owner=self.course_owner
        )

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        self.client.force_authenticate(user=self.user)
        data = {'course_id': self.course.id}
        response = self.client.post('/lms/subscribe/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ✅ Синхронизирован текст сообщения с view
        self.assertEqual(response.data['message'], 'Вы успешно подписались на обновления курса.')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        data = {'course_id': self.course.id}
        response = self.client.post('/lms/subscribe/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ✅ Синхронизирован текст сообщения с view
        self.assertEqual(response.data['message'], 'Вы успешно отписались от курса.')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_serializer_includes_subscription_status(self):
        """Тест, что сериализатор курса включает информацию о подписке"""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)

        # ✅ Исправлен URL: стандартный retrieve роутера
        response = self.client.get(f'/lms/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_course_serializer_not_subscribed(self):
        """Тест, что сериализатор курса показывает отсутствие подписки"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/lms/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])