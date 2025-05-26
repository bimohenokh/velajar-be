from django.db import transaction

from .helpers import submit_attempts_by_quiz_id
from .models import Quiz, QuizStatus


def finish_quiz(quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)

    if quiz.status == QuizStatus.ACTIVE:
        with transaction.atomic():

            quiz.status = QuizStatus.FINISHED
            quiz.save()

            submit_attempts_by_quiz_id(quiz_id)



