from django.conf import settings
from django.urls import path
from .views import CourseView, CourseViewById, CourseSessionView, CourseSessionViewById

urlpatterns = [
    path("", CourseView.as_view(), name="course"),
    path("<int:pk>/", CourseViewById.as_view(), name="course-id"),
    path("course/<int:course_id>/", CourseSessionView.as_view(), name="course-session"),
    path("course/<int:course_id>/session/<int:session_id>/", CourseSessionViewById.as_view(), name="course-session-id"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
