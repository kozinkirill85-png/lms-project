from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для курсов (полный CRUD)
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        """
        Мгновенно создает экземпляр класса разрешений, который будет использоваться для данного запроса
        """
        if self.action in ['create', 'destroy']:
            # Создание и удаление - только модераторы
            permission_classes = [IsAuthenticated, IsModerator]
        elif self.action in ['update', 'partial_update']:
            # Редактирование - модераторы или владелец
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            # Просмотр и список - все авторизованные
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Автоматически привязывает создаваемый курс к текущему пользователю
        """
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        Модераторы видят все курсы, обычные пользователи - только свои
        """
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            # Модераторы видят все курсы
            return Course.objects.all()
        # Обычные пользователи видят только свои курсы
        return Course.objects.filter(owner=user)


# Generic-классы для уроков
class LessonListView(generics.ListAPIView):
    """
    Список всех уроков
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Модераторы видят все уроки, обычные пользователи - только свои
        """
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonDetailView(generics.RetrieveAPIView):
    """
    Детальный просмотр урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


class LessonCreateView(generics.CreateAPIView):
    """
    Создание урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def perform_create(self, serializer):
        """
        Автоматически привязывает создаваемый урок к текущему пользователю
        """
        serializer.save(owner=self.request.user)


class LessonUpdateView(generics.UpdateAPIView):
    """
    Редактирование урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonDestroyView(generics.DestroyAPIView):
    """
    Удаление урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]
