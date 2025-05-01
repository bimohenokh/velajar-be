from rest_framework.fields import IntegerField
from rest_framework.serializers import Serializer, ModelSerializer

from taschoolassistant.chain_notes.models import ChainNote


class ChainNoteParamSerializer(Serializer):
    course_session_id = IntegerField(required=True)


class ChainNoteSerializer(ModelSerializer):
    class Meta:
        model = ChainNote
        fields = "__all__"