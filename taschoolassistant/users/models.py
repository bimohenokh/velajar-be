from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField, Model, CharField, ForeignKey, CASCADE, TextChoices


# Create your models here.
class Role(TextChoices):
    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'


class User(AbstractUser):
    email = EmailField(unique=True)
    role = CharField(max_length=20, choices=Role.choices)


class Permission(Model):
    name = CharField(max_length=100, unique=True)


class RolePermission(Model):
    role = CharField(max_length=20, choices=Role.choices)
    permission = ForeignKey(Permission, on_delete=CASCADE)
