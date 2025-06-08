from rest_framework.exceptions import ValidationError
from rest_framework.fields import (
    IntegerField,
    DateTimeField,
    BooleanField,
    CharField,
    SerializerMethodField,
)
from rest_framework.serializers import Serializer, ModelSerializer

from taschoolassistant.chain_notes.models import ChainNote, ChainNoteTurn
from taschoolassistant.profiles.models import StudentProfile
from taschoolassistant.users.serializers import UserSerializer


class ChainNoteParamSerializer(Serializer):
    course_session_id = IntegerField(required=True)


class ChainNoteSerializer(ModelSerializer):
    class Meta:
        model = ChainNote
        fields = "__all__"
        read_only_fields = ["status"] # TODO status dan course_session gk boleh diubah

    def validate(self, attrs):
        if self.instance:
            if attrs.get("course_session"):
                raise ValidationError(
                    {"course_session": ["course_session cannot be changed"]}
                )
        return super().validate(attrs)


class UpdateChainNoteSerializer(ModelSerializer):
    class Meta:
        model = ChainNote
        fields = "__all__"
        read_only_fields = ["course_session", "status"]


class ChainNoteTurnSerializer(ModelSerializer):
    participant_user = UserSerializer(source="participant.participant", read_only=True)
    participant_image_profile = SerializerMethodField(source="participant.participant.image", read_only=True)

    class Meta:
        model = ChainNoteTurn
        fields = "__all__"

    def get_participant_image_profile(self, obj):
        user = (
            obj.participant.participant
        )  # This assumes participant.participant is a User instance
        try:
            profile = StudentProfile.objects.get(user=user)
            if profile.image_profile:
                return profile.image_profile.url
        except StudentProfile.DoesNotExist:
            pass
        return None

