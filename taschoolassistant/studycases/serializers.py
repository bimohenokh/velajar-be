from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.serializers import Serializer, ModelSerializer

from .models import StudyCase, StudyCaseQuestion, StudyCaseAnswer, StudyCaseAttempt
from ..courses.serializers import CourseParticipantSerializer


class StudyCaseParamSerializer(Serializer):
    course_session_id = IntegerField(required=True)


class StudyCaseSerializer(ModelSerializer):
    class Meta:
        model = StudyCase
        fields = '__all__'
        read_only_fields = ('id', 'course_session')

# Serializers for read and post studycase and question 
class NestedStudyCaseQuestionSerializer(ModelSerializer):
    """
    Serializer for nested StudyCaseQuestion within StudyCaseWithQuestionsSerializer.
    """
    class Meta:
        model = StudyCaseQuestion
        exclude = ['study_case']


class StudyCaseWithQuestionsSerializer(ModelSerializer):
    questions = NestedStudyCaseQuestionSerializer(many=True)
    class Meta:
        model = StudyCase
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        study_case = StudyCase.objects.create(**validated_data)

        question_objs = [
            StudyCaseQuestion(study_case=study_case, **q) for q in questions_data
        ]
        StudyCaseQuestion.objects.bulk_create(question_objs)

        return study_case

    @transaction.atomic
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)

        # Update StudyCase fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle nested update for questions
        if questions_data is not None:
            instance.questions.all().delete()
            question_objs = [
                StudyCaseQuestion(study_case=instance, **q)
                for q in questions_data
            ]
            StudyCaseQuestion.objects.bulk_create(question_objs)

        return instance

#
# # Serializers for read studycase, question, and answer
# class StudyCaseSerializerForAnswer(ModelSerializer):
#     class Meta:
#         model = StudyCase
#         fields = ['id', 'title', 'description', 'image_study_case', 'course_session', 'total_point', 'started_at', 'time_range', 'status']
#
#
# class StudyCaseQuestionSerializerForAnswer(ModelSerializer):
#     study_case = StudyCaseSerializerForAnswer()
#
#     class Meta:
#         model = StudyCaseQuestion
#         fields = ['id', 'question', 'study_case']
#
#
# class StudyCaseAnswerReadSerializers(ModelSerializer):
#     study_case_question = StudyCaseQuestionSerializerForAnswer()
#
#     class Meta:
#         model = StudyCaseAnswer
#         fields = '__all__'
#
#
# #Serializers for post answer
# class StudyCaseAnswerWriteSerializer(ModelSerializer):
#     class Meta:
#         model = StudyCaseAnswer
#         fields = '__all__'


class StudyCaseAttemptSerializer(ModelSerializer):
    participant_user = CourseParticipantSerializer(read_only=True, source="student.participant")

    class Meta:
        model = StudyCaseAttempt
        fields = '__all__'


class NestedStudyCaseAnswerSerializer(ModelSerializer):
    """
    Serializer for nested StudyCaseAnswer within StudyCaseAttemptWithAnswersSerializer.
    """
    class Meta:
        model = StudyCaseAnswer
        exclude = ["study_case_attempt", "point"]


class StudyCaseAttemptWithAnswersSerializer(ModelSerializer):
    participant_user = CourseParticipantSerializer(read_only=True, source="student.participant")
    answers = NestedStudyCaseAnswerSerializer(many=True)

    class Meta:
        model = StudyCaseAttempt
        fields = '__all__'
        read_only_fields = ('id', 'study_case', 'student', 'submitted_at')

    @transaction.atomic
    def create(self, validated_data):
        study_case = self.context.get('study_case')
        answers_data = validated_data.pop('answers', [])
        study_case_attempt = StudyCaseAttempt.objects.create(study_case=study_case, **validated_data)

        answer_objs = [
            StudyCaseAnswer(study_case_attempt=study_case_attempt, **answer) for answer in answers_data
        ]
        StudyCaseAnswer.objects.bulk_create(answer_objs)

        return study_case_attempt

    @transaction.atomic
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)

        # Update StudyCaseAttempt fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle nested update for answers
        if answers_data is not None:
            instance.answers.all().delete()
            answer_objs = [
                StudyCaseAnswer(study_case_attempt=instance, **answer)
                for answer in answers_data
            ]
            StudyCaseAnswer.objects.bulk_create(answer_objs)

        return instance


class EvaluateStudyCaseAnswerSerializer(ModelSerializer):
    """
    Serializer for evaluating StudyCaseAnswer.
    """
    class Meta:
        model = StudyCaseAnswer
        fields = ['id', 'point']
        read_only_fields = ['id']
        extra_kwargs = {
            'point': {'required': True, 'allow_null': False}
        }

    def validate_point(self, value):
        if value is None:
            return value
        if value < 0:
            raise ValidationError("Point cannot be negative.")
        return value

    def validate(self, data):
        if self.instance:
            attempt = self.context.get("attempt")

            if self.instance.study_case_attempt_id != attempt.id:
                raise ValidationError(
                    "This answer does not belong to the given attempt."
                )

            return super().validate(data)

    def create(self, validated_data):
        raise ValidationError("This serializer is for updating existing answers only.")