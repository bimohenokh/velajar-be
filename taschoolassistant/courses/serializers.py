from django.db import transaction
from rest_framework.fields import ChoiceField, IntegerField, BooleanField
from rest_framework.serializers import Serializer, ModelSerializer
from typing_extensions import override

from django.core.files.storage import default_storage

from .models import (
    Course,
    CourseParticipant,
    CourseSession,
    CourseInviteToken,
    ParticipantPoint,
)
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from ..profiles.models import StudentProfile
from ..users.models import Role


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


class CourseSessionFeatureSerializer(Serializer):
    chain_note_id = IntegerField(required=True)
    study_case_id = IntegerField(required=True)
    quiz_id = IntegerField(required=True)
    resource_ids = BooleanField(required=True)


class LeaderboardSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()

    class Meta:
        model = ParticipantPoint
        fields = ["name", "student_class", "point_achieved"]

    def get_name(self, obj):
        # FIXME N+1 query problem kalau dipakai
        return obj.course_participant.participant.nama_lengkap

    def get_student_class(self, obj):
        # FIXME N+1 query problem kalau dipakai
        user = obj.course_participant.participant
        try:
            profile = StudentProfile.objects.get(user=user)
            return profile.student_class
        except StudentProfile.DoesNotExist:
            return "-"


class ParticipantPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantPoint
        fields = "__all__"


class CourseInviteTokenSerializer(ModelSerializer):
    class Meta:
        model = CourseInviteToken
        fields = "__all__"

class CreateCourseInviteTokenSerializerIn(Serializer):
    role = ChoiceField(choices=Role.choices)
