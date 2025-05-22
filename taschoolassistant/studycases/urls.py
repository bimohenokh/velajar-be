from django.urls import path
from .views import StudyCaseView, StudyCaseViewById, StudyCaseAnswerReadView, StudyCaseAnswerPatchView, StudyCaseAnswerWriteView, StudyCaseAnswerReadStudentSubmittedView, \
    StartStudyCaseView

urlpatterns = [
    # url teacher
    path("", StudyCaseView.as_view(), name="study-case"),
    path("session/<int:session_id>/<int:case_id>/", StudyCaseViewById.as_view(), name="study-case-id"),
    path("session/<int:session_id>/submitted/<int:case_id>/", StudyCaseAnswerReadStudentSubmittedView.as_view(), name="student-submitted"),
    path("session/<int:session_id>/answer/<int:student_id>/<int:question_id>/", StudyCaseAnswerPatchView.as_view(), name="study-case-answer-patch"),
    path("<int:case_id>/start", StartStudyCaseView.as_view(), name="start-study-case"),

    
    #url student and teacher
    path("session/<int:session_id>/<int:case_id>/answer/<int:student_id>/", StudyCaseAnswerReadView.as_view(), name="study-case-answer"),

    #url student
    path("", StudyCaseAnswerWriteView.as_view(), name="study-case-answer-post"),
]