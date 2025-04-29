from django.urls import path
from .views import StudyCaseView, StudyCaseViewById, StudyCaseAnswerView, StudyCaseAnswerViewById

urlpatterns = [
    path("session/<int:session_id>/", StudyCaseView.as_view(), name="study-case"),
    path("session/<int:session_id>/<int:case_id>/", StudyCaseViewById.as_view(), name="study-case-id"),
    path("session/<int:session_id>/<int:case_id>/answer/", StudyCaseAnswerView.as_view(), name="study-case-answer"),
    path("session/<int:session_id>/<int:case_id>/answer/<int:answer_id>/", StudyCaseAnswerViewById.as_view(), name="study-case-answer-id")
]