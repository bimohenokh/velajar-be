from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField, Model, CharField, ForeignKey, CASCADE


# Create your models here.
class User(AbstractUser):
    email = EmailField(unique=True)


class Role(Model):
    name = CharField(max_length=50, unique=True)


class Permission(Model):
    name = CharField(max_length=100, unique=True)


class RolePermission(Model):
    role = ForeignKey(Role, on_delete=CASCADE)
    permission = ForeignKey(Permission, on_delete=CASCADE)
