from django.urls import path
from .views import (
    CourseView,
    CourseViewById,
    CourseSessionView,
    CourseSessionViewById,
    InviteCourseWithLink,
    SubmitCourseInviteToken,
    CourseSessionFeatureViewById,
)
from .views import CourseView, CourseViewById, CourseSessionView, CourseSessionViewById, LeaderboardView

urlpatterns = [
    path("", CourseView.as_view(), name="course"),
    path("<int:pk>/", CourseViewById.as_view(), name="course-id"),
    path("<int:course_id>/leaderboards/", LeaderboardView.as_view(), name="leaderboard"),
    path("<int:course_id>/sessions/", CourseSessionView.as_view(), name="course-session"),
    path("<int:course_id>/sessions/<int:session_id>/", CourseSessionViewById.as_view(), name="course-session-id"),
    path("sessions/<int:session_id>/features/", CourseSessionFeatureViewById.as_view(), name="course-session-feature-id"),
    path("<int:course_id>/invite/", InviteCourseWithLink.as_view(), name="course-invite-token"),
    path("invite/<token_str>/", SubmitCourseInviteToken.as_view(), name="course-invite-submit-token"),
]
