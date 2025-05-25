from django.db.models import (
    Model,
    CharField,
    ImageField,
    CASCADE,
    ForeignKey,
    BooleanField,
    TextField,
    FloatField,
    DurationField,
    DateTimeField,
    TextChoices,
    OneToOneField,
)

from taschoolassistant.courses.models import CourseSession, CourseParticipant
from taschoolassistant.studycases.managers import StudyCaseManager, StudyCaseAnswerManager, StudyCaseQuestionManager, \
    StudyCaseAttemptManager


class StudyCaseStatus(TextChoices):
    DRAF = "Draft"
    ACTIVE = "Active"
    FINISHED = "Finished"

class StudyCase(Model):
    title = CharField(max_length=255, null=True, blank=True)
    description = TextField(null=True, blank=True)
    image_study_case = ImageField(
        upload_to='study-case-image/', null=True, blank=True)
    course_session = OneToOneField(CourseSession, on_delete=CASCADE)
    max_point_per_question = FloatField(default=100)
    started_at = DateTimeField(blank=True, null=True)
    time_range= DurationField()
    status = CharField(
        max_length=50,
        choices=StudyCaseStatus,
        default=StudyCaseStatus.DRAF,
    )

    objects = StudyCaseManager()


class StudyCaseQuestion(Model):
    study_case = ForeignKey(StudyCase, on_delete=CASCADE, related_name="questions")
    question = CharField(max_length=255, null=True, blank=True)

    objects = StudyCaseQuestionManager()


class StudyCaseAttempt(Model):
    study_case = ForeignKey(StudyCase, on_delete=CASCADE)
    student = ForeignKey(CourseParticipant, on_delete=CASCADE)
    submitted_at = DateTimeField(blank=True, null=True)
    is_evaluated = BooleanField(default=False)

    objects = StudyCaseAttemptManager()

    @property
    def is_submitted(self):
        if self.submitted_at:
            return True
        return False

    # TODO tambahin property total point


class StudyCaseAnswer(Model):
    study_case_question = ForeignKey(StudyCaseQuestion, on_delete=CASCADE)
    study_case_attempt = ForeignKey(StudyCaseAttempt, on_delete=CASCADE, related_name="answers")
    answer = TextField(blank=True, null=True)
    point = FloatField(blank=True, null=True)

    objects = StudyCaseAnswerManager()

    @property
    def is_evaluated(self):
        if self.point or self.point == 0:
            return True
        return False