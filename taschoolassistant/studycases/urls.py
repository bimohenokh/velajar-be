from django.urls import path
from .views import StudyCaseView, StudyCaseViewById, StudyCaseAnswerReadView, StudyCaseAnswerPatchView, StudyCaseAnswerWriteView, StudyCaseAnswerReadStudentSubmittedView

urlpatterns = [
    path("session/<int:session_id>/", StudyCaseView.as_view(), name="study-case"),
    path("session/<int:session_id>/<int:case_id>/", StudyCaseViewById.as_view(), name="study-case-id"),
    path("session/<int:session_id>/<int:case_id>/answer/<int:check_id>/", StudyCaseAnswerReadView.as_view(), name="study-case-answer"),
    path("case/<int:case_id>/", StudyCaseAnswerReadStudentSubmittedView.as_view(), name="student-submitted"),
    path("session/<int:session_id>/answer/<int:check_id>/<int:question_id>/", StudyCaseAnswerPatchView.as_view(), name="study-case-answer-patch"),
    path("", StudyCaseAnswerWriteView.as_view(), name="study-case-answer-post"),
]