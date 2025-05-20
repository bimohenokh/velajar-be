from django.db import transaction
from typing_extensions import override

from django.core.files.storage import default_storage

from .models import StudyCase, StudyCaseQuestion, StudyCaseAnswer
from rest_framework import serializers


# Serializers for read and post studycase and question 
class StudyCaseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyCaseQuestion
        fields = ['id', 'question']
class StudyCaseSerializer(serializers.ModelSerializer):
    studycasequestion_set = StudyCaseQuestionSerializer(many=True)
    class Meta:
        model = StudyCase
        fields = ['id', 'title', 'description', 'image_study_case', 'course_session', 'total_point', 'started_at', 'time_range', 'status', 'studycasequestion_set']

    def create(self, validated_data):
        questions_data = validated_data.pop('studycasequestion_set')
        study_case = StudyCase.objects.create(**validated_data)
        for question_data in questions_data:
            StudyCaseQuestion.objects.create(study_case=study_case, **question_data)
        return study_case
    
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('studycasequestion_set', [])

        # Update StudyCase fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle nested update for studycasequestion_set
        existing_ids = [q.id for q in instance.studycasequestion_set.all()]
        sent_ids = [q.get('id') for q in questions_data if q.get('id')]

        # Delete questions not in request
        for q in instance.studycasequestion_set.all():
            if q.id not in sent_ids:
                q.delete()

        # Create or update
        for question_data in questions_data:
            question_id = question_data.get('id', None)
            if question_id and question_id in existing_ids:
                question = StudyCaseQuestion.objects.get(id=question_id, study_case=instance)
                question.question = question_data['question']
                question.save()
            else:
                StudyCaseQuestion.objects.create(study_case=instance, **question_data)

        return instance



# Serializers for read studycase, question, and answer 
class StudyCaseSerializerForAnswer(serializers.ModelSerializer):
    class Meta:
        model = StudyCase
        fields = ['id', 'title', 'description', 'image_study_case', 'course_session', 'total_point', 'started_at', 'time_range', 'status']
class StudyCaseQuestionSerializerForAnswer(serializers.ModelSerializer):
    study_case = StudyCaseSerializerForAnswer()

    class Meta:
        model = StudyCaseQuestion
        fields = ['id', 'question', 'study_case']
class StudyCaseAnswerReadSerializers(serializers.ModelSerializer):
    study_case_question = StudyCaseQuestionSerializerForAnswer()

    class Meta:
        model = StudyCaseAnswer
        fields = '__all__'



#Serializers for post answer
class StudyCaseAnswerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyCaseAnswer
        fields = '__all__'
