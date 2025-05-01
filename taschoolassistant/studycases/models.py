from enum import Enum
from django.db.models import Model, CharField, ImageField, CASCADE, ForeignKey, BooleanField, FileField, TextField, FloatField, DateField, DurationField, DateTimeField
from taschoolassistant.courses.models import CourseSession
from taschoolassistant.users.models import User
from taschoolassistant.studycases.managers import StudyCaseManager, StudyCaseAnswerManager, StudyCaseQuestionManager
from django.contrib.auth import get_user_model


User = get_user_model()


class StatusStudyCases(Enum):
    DRAF = 'Draft'
    ACTIVE =  'Active'
    FINISHED = 'Finished'

class StudyCase(Model):
    title = CharField(max_length=255, null=True, blank=True)
    description = TextField(null=True, blank=True)
    image_study_case = ImageField(
        upload_to='study-case-image/', null=True, blank=True)
    course_session = ForeignKey(CourseSession, on_delete=CASCADE)
    total_point = FloatField(default=100)
    started_at = DateTimeField(blank=True, null=True)
    time_range= DurationField(blank=True, null=True)
    status = CharField(
        max_length=50,
        choices=[(status.value, status.name) for status in StatusStudyCases],
        default=StatusStudyCases.DRAF.value,
    )

    objects = StudyCaseManager()


class StudyCaseQuestion(Model):
    study_case = ForeignKey(StudyCase, on_delete=CASCADE)
    question = CharField(max_length=255, null=True, blank=True)

    objects = StudyCaseQuestionManager()


class StudyCaseAnswer(Model):
    student = ForeignKey(User, on_delete=CASCADE)
    answer = TextField(blank=True, null=True)
    started_at = DateTimeField(blank=True, null=True)
    submitted_at = DateTimeField(blank=True, null=True)
    point = FloatField(default=0)
    is_submitted = BooleanField(default=False)
    is_evaluated = BooleanField(default=False)
    study_case_question = ForeignKey(StudyCaseQuestion, on_delete=CASCADE)


    objects = StudyCaseAnswerManager()