# quizzes/serializers.py
from django.utils import timezone
from rest_framework import serializers
from .models import Quiz, Question, Option, QuizAttempt, Answer
from ..users.serializers import UserSerializer


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

class StudentOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']

class StudentQuestionSerializer(serializers.ModelSerializer):
    options = StudentOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'options']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'options']

    def validate(self, data):
        if 'options' in data:
            options = data.get('options', [])
            if len(options) < 2:
                raise serializers.ValidationError("A question must have at least two options.")

            correct_options = [opt for opt in options if opt.get('is_correct')]
            q_type = data.get('type')

            if q_type == 'single' and len(correct_options) != 1:
                raise serializers.ValidationError("Single choice questions must have exactly one correct option.")
            elif q_type == 'multiple' and len(correct_options) < 2:
                raise serializers.ValidationError("Multiple choice questions must have at least two correct options.")

        return data

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        quiz = self.context['quiz']
        validated_data.pop('quiz', None)  # buang jika sudah ada
        question = Question.objects.create(quiz=quiz, **validated_data)
        for opt in options_data:
            Option.objects.create(question=question, **opt)
        return question
    
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        instance.text = validated_data.get('text', instance.text)
        instance.type = validated_data.get('type', instance.type)
        instance.save()

        if options_data is not None:
            # Hapus semua option lama
            instance.options.all().delete()
            # Buat option baru
            for opt_data in options_data:
                Option.objects.create(question=instance, **opt_data)

        return instance


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'course_session', 'total_points', 'time_range', 'status', 'started_at']
        read_only_fields = ['id', 'started_at']
    
    def update(self, instance, validated_data):

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.course_session = validated_data.get('course_session', instance.course_session)
        instance.total_points = validated_data.get('total_points', instance.total_points)
        instance.time_range = validated_data.get('time_range', instance.time_range)
        instance.status = validated_data.get('status', instance.status)

        instance.save()
        return instance


class FullQuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = "__all__"
        read_only_fields = ['id', 'started_at']

    def create(self, validated_data):
        raise serializers.ValidationError("This serializer is read-only and cannot be used to create instances.")

    def update(self, instance, validated_data):
        raise serializers.ValidationError("This serializer is read-only and cannot be used to update instances.")

class AnswerSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Option.objects.all()
    )

    class Meta:
        model = Answer
        fields = ['question', 'selected_options']
    
    def validate(self, data):
        question = data.get('question')
        selected_options = data.get('selected_options')

        if not question:
            raise serializers.ValidationError("Question is required.")

        if question.type == 'single':
            if len(selected_options) != 1:
                raise serializers.ValidationError("Single choice questions must have exactly one selected option.")

        # Optional: pastikan selected options benar-benar milik pertanyaannya
        options = Option.objects.filter(question=question)
        valid_option_ids = set(options.values_list('id', flat=True))
        for option in selected_options:
            if option.id not in valid_option_ids:
                raise serializers.ValidationError(f"Option {option.id} does not belong to the question.")

        return data

class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, write_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'student', 'submitted_at', 'score', 'answers']
        read_only_fields = ['score', 'submitted_at']

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])

        instance.score = self.calculate_score(instance, answers_data)
        instance.submitted_at = timezone.now()
        instance.is_submitted = True
        instance.save()
        return instance

    def calculate_score(self, attempt, answers):
        total_questions = attempt.quiz.questions.count()
        correct = 0

        if total_questions == 0:
            return 0
        for answer in answers:
            question = answer['question']
            if isinstance(question, Question):
                question_id = question.id
            else:
                question_id = question
            selected_option_ids = selected_option_ids = set(
                opt.id if isinstance(opt, Option) else opt
                for opt in answer['selected_options']
            )


            question = Question.objects.get(id=question_id)
            correct_option_ids = set(question.options.filter(is_correct=True).values_list('id', flat=True))

            if selected_option_ids == correct_option_ids:
                correct += 1
        return (correct / total_questions) * attempt.quiz.total_points


class AllQuizAttemptSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    class Meta:
        model = QuizAttempt
        fields = "__all__"

    def create(self, validated_data):
        raise serializers.ValidationError("This serializer is read-only and cannot be used to create instances.")

    def update(self, instance, validated_data):
        raise serializers.ValidationError("This serializer is read-only and cannot be used to update instances.")


class QuizAttemptFullDetailSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = "__all__"
        read_only_fields = ['id', 'quiz', 'student', 'started_at', 'submitted_at', 'score', 'is_submitted']

    def create(self, validated_data):
        raise serializers.ValidationError("This serializer is read-only and cannot be used to create instances.")

    def update(self, instance, validated_data):
        raise serializers.ValidationError("This serializer is read-only and cannot be used to update instances.")


class MyQuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = "__all__"
        read_only_fields = ['id', 'quiz', 'student', 'submitted_at', 'score']
