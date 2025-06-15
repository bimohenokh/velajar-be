# quizzes/urls.py
from django.urls import path
from .views import (
    QuizView,
    QuizDetailView,
    QuestionByQuizIdView,
    StartQuizView,
    StopQuizView,
    AnswerView,
    StartAttemptView,
    SubmitQuizView,
    QuestionDetailView,
    MyQuizAttemptView,
    QuizAttemptView,
)

urlpatterns = [
    path('', QuizView.as_view(), name='quiz'),
    path('<int:quiz_id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('<int:quiz_id>/questions/', QuestionByQuizIdView.as_view(), name='quiz-questions'),
    path("questions/<int:question_id>/", QuestionDetailView.as_view(), name='question-detail'),
    path('<int:quiz_id>/start/', StartQuizView.as_view(), name='start-quiz'),
    path('<int:quiz_id>/stop/', StopQuizView.as_view(), name='stop-quiz'),
    path('answer/', AnswerView.as_view(), name='answer'),
    path('<int:quiz_id>/start-attempt/', StartAttemptView.as_view(), name='start-attempt'),
    path('<int:quiz_id>/attempts/', QuizAttemptView.as_view(), name='quiz-attempts'),
    path("<int:quiz_id>/attempts/me/", MyQuizAttemptView.as_view(), name="my-quiz-attempt"),
    path('submit/', SubmitQuizView.as_view(), name='submit-quiz'),
]
