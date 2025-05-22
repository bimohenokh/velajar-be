
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.serializers import Serializer

from .models import Resource

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"
        read_only_fields = ("id", "course_session")

    def validate(self, attrs):
        # Inject course_session if not provided
        course_session = self.context.get("course_session")
        if not self.instance and course_session:
            attrs["course_session"] = course_session
        return super().validate(attrs)

class ResourceParamSerializer(Serializer):
    course_session_id = IntegerField(required=True)