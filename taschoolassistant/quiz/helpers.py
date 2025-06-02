from django.db import transaction
from django.db.models import F
from django.utils import timezone

from taschoolassistant.courses.models import ParticipantPoint, Course, CourseParticipant
from taschoolassistant.quiz.models import QuizAttempt


def calculate_quiz_attempt_score(quiz_attempt):
    attempt_answers = quiz_attempt.answers.all()
    quiz = quiz_attempt.quiz

    quiz_total_points = quiz.total_points

    point_received = 0
    for answer in attempt_answers:
        question = answer.question
        selected_option_ids = set(answer.selected_options.values_list('id', flat=True))
        correct_option_ids = set(question.options.filter(is_correct=True).values_list('id', flat=True))

        if selected_option_ids == correct_option_ids:
            point_received += (quiz_total_points / quiz.questions.count())

    return point_received


def submit_attempts_by_quiz_id(quiz_id):
    """
    Function to submit attempts by quiz ID.
    """
    # Logic to submit attempts by quiz ID
    attempts = QuizAttempt.objects.filter(
        quiz_id=quiz_id
    )
    for attempt in attempts:
        if not attempt.is_submitted:
            attempt.submitted_at = timezone.now()
            attempt.is_submitted = True
            # Decide if/how to score auto-submitted attempts
            # attempt.score = ...

            # logic untuk menghitung score attempt
            attempt.score = calculate_quiz_attempt_score(attempt)

        # score attempt dihitung ke leaderboard
        course_participant = CourseParticipant.objects.get(
            participant_id=attempt.student_id,
            course_id=attempt.quiz.course_session.course_id
        )
        ParticipantPoint.objects.filter(
            course_participant=course_participant
        ).update(
            point_achieved=F("point_achieved") + attempt.score
        )


    QuizAttempt.objects.bulk_update(attempts, ['submitted_at', 'is_submitted'])

