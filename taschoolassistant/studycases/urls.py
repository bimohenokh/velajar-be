from django.urls import path
from .views import (
    StudyCaseView,
    StudyCaseViewById,
    StartStudyCaseView,
    StudyCaseAttemptView,
    StopStudyCaseView,
    EvaluateStudyCaseAnswerView,
)

urlpatterns = [
    path("", StudyCaseView.as_view(), name="study-case"),
    path("<int:case_id>/", StudyCaseViewById.as_view(), name="study-case-id"),
    # path("session/<int:session_id>/submitted/<int:case_id>/", StudyCaseAnswerReadStudentSubmittedView.as_view(), name="student-submitted"),
    # path("session/<int:session_id>/answer/<int:student_id>/<int:question_id>/", StudyCaseAnswerPatchView.as_view(), name="study-case-answer-patch"),
    # path("<case_id>/answers/", StudyCaseAnswerView.as_view(), name="study-case-answer"),
    path("<int:case_id>/start", StartStudyCaseView.as_view(), name="start-study-case"),
    path("<int:case_id>/stop", StopStudyCaseView.as_view(), name="stop-study-case"),
    path("<int:case_id>/attempts/", StudyCaseAttemptView.as_view(), name="study-case-attempts"),
    path("attempts/<int:attempt_id>/", StartStudyCaseView.as_view(), name="study-case-attempt-id"),
    path("attempts/answers/evaluate/", EvaluateStudyCaseAnswerView.as_view(), name="evaluate-study-case-attempt"),

    
    # path("session/<int:session_id>/<int:case_id>/answer/<int:student_id>/", StudyCaseAnswerReadView.as_view(), name="study-case-answer"),

    # path("", StudyCaseAnswerWriteView.as_view(), name="study-case-answer-post"),
]