from django.db import models

from django.contrib.auth import get_user_model
from django.db.models import TextChoices

from taschoolassistant.courses.models import CourseSession

User = get_user_model()

class QuizStatus(TextChoices):
    DRAFT = 'Draft', 'Draft'
    ACTIVE = 'Active', 'Active'
    FINISHED = 'Finished', 'Finished'


class Quiz(models.Model):
    course_session = models.OneToOneField(CourseSession, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    total_points = models.FloatField(default=100)
    started_at = models.DateTimeField(blank=True, null=True)
    time_range = models.DurationField()
    status = models.CharField(max_length=10, choices=QuizStatus.choices, default=QuizStatus.DRAFT)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes_created')

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    type = models.CharField(max_length=10, choices=[('single', 'Single'), ('multiple', 'Multiple')])

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True, default=0)
    is_submitted = models.BooleanField(default=False)

class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(Option)