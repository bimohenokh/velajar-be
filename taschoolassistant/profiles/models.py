from enum import Enum
from django.db import models
from django.contrib.auth import get_user_model
from taschoolassistant.users.models import User
from django.db.models import Model, CharField, ImageField, DateField, CASCADE, ForeignKey, BooleanField, FileField
from .managers import StudentProfileManager, TeacherProfileManager

# Create your models here.
User = get_user_model()

class JenjangKelas(Enum):
    SMA_KELAS_1 = "SMA Kelas 1"
    SMA_KELAS_2 = "SMA Kelas 2"
    SMA_KELAS_3 = "SMA Kelas 3"

class TeacherProfile(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    image_profile = ImageField(
        upload_to='teacher-profile/', null=True, blank=True)
    dateOfBirth = DateField(null=True, blank=True)
    school = CharField(max_length=255, null=True, blank=True)

    objects = TeacherProfileManager()


class StudentProfile(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    image_profile = ImageField(
        upload_to='teacher-profile/', null=True, blank=True)
    dateOfBirth = DateField(null=True, blank=True)
    school = CharField(max_length=255, null=True, blank=True)
    student_class = CharField(
        max_length=50,
        choices=[(role.value, role.name) for role in JenjangKelas],
        default=JenjangKelas.SMA_KELAS_1.value,
    )


    objects = StudentProfileManager()