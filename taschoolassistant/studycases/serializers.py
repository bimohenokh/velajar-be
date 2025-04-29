from django.db import transaction
from typing_extensions import override

from django.core.files.storage import default_storage

from .models import StudyCase, StudyCaseAnswer
from rest_framework import serializers


class StudyCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyCase
        fields = "__all__"



class StudyCaseAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyCaseAnswer
        fields = "__all__"
