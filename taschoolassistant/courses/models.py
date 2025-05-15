from enum import Enum

from django.contrib.auth import get_user_model
from django.db.models import (
    Model,
    CharField,
    ImageField,
    CASCADE,
    ForeignKey,
    BooleanField,
    FileField,
    DateTimeField,
    IntegerField, TextField,
)

from taschoolassistant.courses.managers import CourseManager, CourseInstructorManager, CourseParticipantManager, \
    CourseSessionManager, CourseSessionResourceManager
from taschoolassistant.users.models import Role

# Create your models here.
User = get_user_model()


class JenjangKelas(Enum):
    SMA_KELAS_1 = "SMA Kelas 1"
    SMA_KELAS_2 = "SMA Kelas 2"
    SMA_KELAS_3 = "SMA Kelas 3"


class Course(Model):
    name = CharField(max_length=255)
    description = CharField(max_length=255, null=True, blank=True)
    image_banner = ImageField(
        upload_to='courses-banner/', null=True, blank=True)
    jenjang_kelas = CharField(
        max_length=50,
        choices=[(role.value, role.name) for role in JenjangKelas],
        default=JenjangKelas.SMA_KELAS_1.value,
    )

    objects = CourseManager()


class CourseParticipant(Model):
    course = ForeignKey(Course, on_delete=CASCADE)
    participant = ForeignKey(User, on_delete=CASCADE)
    is_participating = BooleanField(default=True)

    objects = CourseParticipantManager()

    @property
    def is_teacher(self):
        return hasattr(self, 'courseinstructor')


class CourseInstructor(Model):
    course_participant = OneToOneField(CourseParticipant, on_delete=CASCADE)
    is_owner = BooleanField(default=False)

    objects = CourseInstructorManager()


class CourseSession(Model):
    course = ForeignKey(Course, on_delete=CASCADE)
    name = CharField(max_length=255)
    description = CharField(max_length=255, null=True, blank=True)

    objects = CourseSessionManager()


class CourseSessionResource(Model):
    course_session = ForeignKey(CourseSession, on_delete=CASCADE)
    content = FileField(upload_to='courses-resources/')

    objects = CourseSessionResourceManager()


class CourseInviteToken(Model):
    course = ForeignKey(Course, on_delete=CASCADE)
    token = CharField(max_length=255, unique=True)
    role = CharField(choices=Role.choices, max_length=20)
    expired_at = DateTimeField()
