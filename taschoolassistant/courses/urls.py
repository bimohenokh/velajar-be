from django.conf import settings
from django.urls import path
from .views import CourseView, CourseViewById
from django.conf.urls.static import static

urlpatterns = [
    path("", CourseView.as_view(), name="course"),
    path("<int:pk>", CourseViewById.as_view(), name="course-id"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
