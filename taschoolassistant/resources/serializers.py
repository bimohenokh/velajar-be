
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.serializers import Serializer

from .models import Resource

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'

    def update(self, instance, validated_data):

        # Raise error if course_session is being changed
        if 'course_session' in validated_data and validated_data['course_session'] != instance.course_session:
            raise ValidationError({"course_session": "You cannot change the course_session once set."})
        return super().update(instance, validated_data)

    def validate(self, attrs):
        # Inject course_session if not provided
        course_session = self.context.get('course_session')
        if course_session:
            attrs['course_session'] = course_session
        return attrs

class ResourceParamSerializer(Serializer):
    session_id = IntegerField(required=True)