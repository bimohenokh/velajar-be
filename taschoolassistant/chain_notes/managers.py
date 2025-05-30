from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Manager
from django.utils import timezone
from rest_framework.exceptions import NotFound


class ChainNoteManager(Manager):
    def get_queryset(self):
        return super().get_queryset()


class ChainNoteTurnManager(Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("chain_note")

    def filter_available_turn_by_chain_note(self, chain_note):
        current_time = timezone.now()

        return self.filter(
            chain_note_id=chain_note
        ).filter(
            started_at__gt=current_time-chain_note.duration_per_participant,
            is_skipped=False,
        ).order_by("id")

    async def aget_current_turn_by_chain_note(self, chain_note):
        return await self.filter_available_turn_by_chain_note(chain_note).order_by(
            "id"
        ).select_related(
            "participant__participant"
        ).afirst()
