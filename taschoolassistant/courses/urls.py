from django.urls import path
from .views import CourseView, CourseViewById, CourseSessionView, CourseSessionViewById, LeaderboardView

urlpatterns = [
    path("", CourseView.as_view(), name="course"),
    path("<int:pk>/", CourseViewById.as_view(), name="course-id"),
    path("<int:course_id>/session/", CourseSessionView.as_view(), name="course-session"),
    path("<int:course_id>/leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("<int:course_id>/session/<int:session_id>/", CourseSessionViewById.as_view(), name="course-session-id"),
]
