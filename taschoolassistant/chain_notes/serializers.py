from rest_framework.fields import IntegerField, DateTimeField, BooleanField, CharField
from rest_framework.serializers import Serializer, ModelSerializer

from taschoolassistant.chain_notes.models import ChainNote


class ChainNoteParamSerializer(Serializer):
    course_session_id = IntegerField(required=True)


class ChainNoteSerializer(ModelSerializer):
    class Meta:
        model = ChainNote
        fields = "__all__"
        read_only_fields = ["status"] # TODO status dan course_session gk boleh diubah


class ChainNoteTurnLongPollingSerializer(Serializer):
    chain_note_id = IntegerField(required=False)
    started_at = DateTimeField(required=False)
    finished_at = DateTimeField(required=False)
    is_turn_reached = IntegerField(required=False)
    is_skipped = IntegerField(required=False)
    participant_id = IntegerField(required=False)
    pariticipant_username = CharField(source="participant.participant.username", required=False)
    # TODO buat nama panjang participant nunggu dari profile si
    is_chain_note_finished = BooleanField(default=False)


# class StartChainNoteSerializer(ModelSerializer):
#     class Meta:
#         model = ChainNote
#         fields = "__all__"