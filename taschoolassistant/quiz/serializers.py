# quizzes/serializers.py
from datetime import timezone
from rest_framework import serializers
from .models import Quiz, Question, Option, QuizAttempt, Answer

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'options']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'course_session' 'total_points', 'time_range', 'status']

class AnswerSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Option.objects.all()
    )

    class Meta:
        model = Answer
        fields = ['question', 'selected_options']

class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, write_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'student', 'submitted_at', 'score', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        quiz_id = validated_data['quiz']
        quiz = Quiz.objects.get(id=quiz_id)
        attempt = QuizAttempt.objects.get(quiz=quiz)

        attempt.score = self.calculate_score(attempt, answers_data)
        attempt.submitted_at = timezone.now()
        attempt.is_submitted = True
        attempt.save()
        return attempt

    def calculate_score(self, attempt, answers):
        questions = Question.objects.get(quiz=attempt.quiz)
        correct = 0
        total = questions.count()

        if total == 0:
            return 0
        for answer in answers.all():
            correct_options = set(answer.question.options.filter(is_correct=True).values_list('id', flat=True))
            selected_options = set(answer.selected_options.all().values_list('id', flat=True))
            if correct_options == selected_options:
                correct += 1
        return (correct / total) * attempt.quiz.total_points
