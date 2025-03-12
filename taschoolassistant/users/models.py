from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField


# Create your models here.

class User(AbstractUser):
    email = EmailField(unique=True)
