from django.urls import path
from .views import (
    StudyCaseView,
    StudyCaseViewById,
    StartStudyCaseView,
    StudyCaseAttemptView,
    StopStudyCaseView,
    EvaluateStudyCaseAnswerView,
    StudyCaseAttemptByIdView,
    MyStudyCaseAttemptView,
)

urlpatterns = [
    path("", StudyCaseView.as_view(), name="study-case"),
    path("<int:case_id>/", StudyCaseViewById.as_view(), name="study-case-id"),
    path("<int:case_id>/start/", StartStudyCaseView.as_view(), name="start-study-case"),
    path("<int:case_id>/stop/", StopStudyCaseView.as_view(), name="stop-study-case"),
    path("<int:case_id>/attempts/", StudyCaseAttemptView.as_view(), name="study-case-attempts"),
    path("<int:case_id>/attempts/me/", MyStudyCaseAttemptView.as_view(), name="my-study-case-attempt"),
    path("attempts/<int:attempt_id>/", StudyCaseAttemptByIdView.as_view(), name="study-case-attempt-id"),
    path("attempts/<int:attempt_id>/answers/evaluate/", EvaluateStudyCaseAnswerView.as_view(), name="evaluate-study-case-attempt"),
]