from django.urls import path
from .views import CourseView, CourseViewById

urlpatterns = [
    path("", CourseView.as_view(), name="course"),
    path("<int:pk>/", CourseViewById.as_view(), name="course-id"),
]
