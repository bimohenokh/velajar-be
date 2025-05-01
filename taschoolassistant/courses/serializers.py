from django.db import transaction
from typing_extensions import override

from django.core.files.storage import default_storage

from .models import Course, CourseParticipant, CourseSession, ParticipantPoint
from taschoolassistant.users.serializers import UserSerializer

from rest_framework import serializers


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"



class CourseParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseParticipant
        fields = "__all__"


class CourseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSession
        fields = "__all__"

class LeaderboardSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ParticipantPoint
        fields = ['name', 'point_achieved']

    def get_name(self, obj):
        return obj.course_participant.participant.get_full_name() or obj.course_participant.participant.username