from django.contrib.auth import get_user_model
from django.db.models import Model, CharField, ImageField, CASCADE, ForeignKey, BooleanField, FileField

from taschoolassistant.courses.managers import CourseManager, CourseInstructorManager, CourseParticipantManager, \
    CourseSessionManager, CourseSessionResourceManager

# Create your models here.
User = get_user_model()


class Course(Model):
    name = CharField(max_length=255)
    description = CharField(max_length=255, null=True, blank=True)
    image_banner = ImageField(upload_to='courses-banner/', null=True, blank=True)

    objects = CourseManager()


class CourseInstructor(Model):
    course = ForeignKey(Course, on_delete=CASCADE)
    teacher = ForeignKey(User, on_delete=CASCADE)
    is_participating = BooleanField(default=True)
    is_owner = BooleanField(default=False)

    objects = CourseInstructorManager()


class CourseParticipant(Model):
    course = ForeignKey(Course, on_delete=CASCADE)
    student = ForeignKey(User, on_delete=CASCADE)
    is_participating = BooleanField(default=True)

    objects = CourseParticipantManager()


class CourseSession(Model):
    course = ForeignKey(Course, on_delete=CASCADE)
    name = CharField(max_length=255)
    description = CharField(max_length=255, null=True, blank=True)

    objects = CourseSessionManager()


class CourseSessionResource(Model):
    course_session = ForeignKey(CourseSession, on_delete=CASCADE)
    content = FileField(upload_to='courses-resources/')

    objects = CourseSessionResourceManager()

