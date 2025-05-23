from django.utils import timezone

from taschoolassistant.quiz.models import QuizAttempt


def submit_attempts_by_quiz_id(quiz_id):
    """
    Function to submit attempts by quiz ID.
    """
    # Logic to submit attempts by quiz ID
    pending_attempts = QuizAttempt.objects.filter(
        quiz_id=quiz_id, is_submitted=False
    )
    for attempt in pending_attempts:
        attempt.submitted_at = timezone.now()
        attempt.is_submitted = True
        # Decide if/how to score auto-submitted attempts
        # attempt.score = ...
    QuizAttempt.objects.bulk_update(pending_attempts, ['submitted_at', 'is_submitted'])