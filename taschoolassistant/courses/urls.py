from django.urls import path
from .views import (
    CourseView,
    CourseViewById,
    CourseSessionView,
    CourseSessionViewById,
    InviteCourseWithLink,
)

urlpatterns = [
    path("", CourseView.as_view(), name="course"),
    path("<int:pk>/", CourseViewById.as_view(), name="course-id"),
    path("course/<int:course_id>/", CourseSessionView.as_view(), name="course-session"),
    path("course/<int:course_id>/session/<int:session_id>/", CourseSessionViewById.as_view(), name="course-session-id"),
    path("<int:course_id>/invite-token/", InviteCourseWithLink.as_view(), name="course-invite-token"),
]
