from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Стандартный пагинатор с настройками
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр запроса для изменения размера страницы
    max_page_size = 100  # Максимальный размер страницы


class LessonPagination(PageNumberPagination):
    """
    Пагинатор для уроков
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class CoursePagination(PageNumberPagination):
    """
    Пагинатор для курсов
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100