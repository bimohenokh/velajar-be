from django.db.models import (
    Model,
    TextField,
    IntegerChoices,
    IntegerField,
    OneToOneField,
    RESTRICT,
    DurationField,
)
from taschoolassistant.chain_notes.managers import ChainNoteManager
from taschoolassistant.courses.models import CourseSession


class ChainNote(Model):
    class Status(IntegerChoices):
        DRAFT = 0, "Draft"
        ONGOING = 1, "Ongoing"
        FINISHED = 2, "Finished"

    course_session = OneToOneField(CourseSession, on_delete=RESTRICT)
    description = TextField()
    duration_per_participant = DurationField()
    status = IntegerField(choices=Status, default=Status.DRAFT)

    objects = ChainNoteManager()

