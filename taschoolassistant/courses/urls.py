from django.urls import path
from .views import CourseView, CourseViewById, CourseSessionView, CourseSessionViewById, LeaderboardView

urlpatterns = [
    path("", CourseView.as_view(), name="course"),
    path("<int:pk>/", CourseViewById.as_view(), name="course-id"),
    path("course/<int:course_id>/", CourseSessionView.as_view(), name="course-session"),
    path("leaderboard/<int:course_id>/", LeaderboardView.as_view(), name="leaderboard"),
    path("course/<int:course_id>/session/<int:session_id>/", CourseSessionViewById.as_view(), name="course-session-id"),
]
