from django.db import transaction
from rest_framework.fields import ChoiceField
from rest_framework.serializers import Serializer, ModelSerializer
from typing_extensions import override

from django.core.files.storage import default_storage

from .models import Course, CourseParticipant, CourseSession, CourseInviteToken
from rest_framework import serializers

from ..users.models import Role


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

    @override
    def update(self, instance, validated_data):
        """Update instance and delete old image file if a new one is provided"""
        # TODO misal kalau user upload gambar tapi nama file sama dengan yang udah ada
        # TODO kalau bulk_update kgk bakal diexecute
        # TODO handle transaction
        old_image_path = instance.image_banner.path if instance.image_banner else None
        new_image = validated_data.get("image_banner", None)

        with transaction.atomic():  # Ensure database update is atomic
            updated_instance = super().update(instance, validated_data)

            # Only delete the old image if a new one is uploaded and is different
            if new_image and old_image_path and old_image_path != updated_instance.image_banner.path:
                if default_storage.exists(old_image_path):
                    try:
                        default_storage.delete(old_image_path)
                    except Exception as e:
                        print(f"Failed to delete old image: {e}")

        return updated_instance


class CourseParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseParticipant
        fields = "__all__"


class CourseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSession
        fields = "__all__"


class CourseInviteTokenSerializer(ModelSerializer):
    class Meta:
        model = CourseInviteToken
        fields = "__all__"

class CreateCourseInviteTokenSerializerIn(Serializer):
    role = ChoiceField(choices=Role.choices)
