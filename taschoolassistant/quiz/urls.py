# quizzes/urls.py
from django.urls import path
from .views import QuizView, QuizDetailView, QuestionByQuizIdView, StartQuizView, StopQuizView, SaveAnswerView, StartAttemptView, SubmitQuizView

urlpatterns = [
    path('', QuizView.as_view(), name='quiz'),
    path('<int:quiz_id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('<int:quiz_id>/questions/', QuestionByQuizIdView.as_view(), name='quiz-questions'),
    path('<int:quiz_id>/start/', StartQuizView.as_view(), name='start-quiz'),
    path('<int:quiz_id>/stop/', StopQuizView.as_view(), name='stop-quiz'),
    path('save-answer/', SaveAnswerView.as_view(), name='save-answer'),
    path('start-attempt/', StartAttemptView.as_view(), name='start-attempt'),
    path('submit/', SubmitQuizView.as_view(), name='submit-quiz'),
]
