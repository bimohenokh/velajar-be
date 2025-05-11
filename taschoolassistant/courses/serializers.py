from django.db import transaction
from typing_extensions import override

from django.core.files.storage import default_storage

from .models import Course, CourseParticipant, CourseSession, ParticipantPoint
from taschoolassistant.users.serializers import UserSerializer
from taschoolassistant.profiles.models import StudentProfile
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist


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
    student_class = serializers.SerializerMethodField()

    class Meta:
        model = ParticipantPoint
        fields = ['name', 'student_class', 'point_achieved']

    def get_name(self, obj):
        return obj.course_participant.participant.nama_lengkap

    def get_student_class(self, obj):
        user = obj.course_participant.participant
        try:
            profile = StudentProfile.objects.get(user=user)
            return profile.student_class
        except StudentProfile.DoesNotExist:
            return "-"