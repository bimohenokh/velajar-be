from django.db.models import (
    Model,
    TextField,
    IntegerChoices,
    IntegerField,
    OneToOneField,
    DurationField,
    ForeignKey,
    DateTimeField,
    BooleanField,
    CASCADE,
)
from django.utils import timezone

from taschoolassistant.chain_notes.managers import (
    ChainNoteManager,
    ChainNoteTurnManager,
)
from taschoolassistant.courses.models import CourseSession, CourseParticipant


class ChainNote(Model):
    class Status(IntegerChoices):
        DRAFT = 0, "Draft"
        ONGOING = 1, "Ongoing"
        FINISHED = 2, "Finished"

    course_session = OneToOneField(CourseSession, on_delete=CASCADE)
    description = TextField()
    duration_per_participant = DurationField()
    status = IntegerField(choices=Status, default=Status.DRAFT)

    objects = ChainNoteManager()

    @property
    def has_not_started(self):
        return self.status == self.Status.DRAFT

    @property
    def is_ended(self):
        return self.status == ChainNote.Status.FINISHED


class ChainNoteTurn(Model):
    chain_note = ForeignKey(ChainNote, on_delete=CASCADE, related_name='turns')
    participant = ForeignKey(CourseParticipant, on_delete=CASCADE)
    started_at = DateTimeField(null=True, blank=True)
    is_skipped = BooleanField(default=False)

    objects = ChainNoteTurnManager()

    @property
    def is_available(self):
        return self.is_skipped or timezone.now() > self.finished_at

    @property
    def finished_at(self):
        """
        Always use select_related "chain_note"
        """
        if not self.started_at:
            return None

        duration = self.chain_note.duration_per_participant
        return self.started_at + duration
