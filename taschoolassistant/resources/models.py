from enum import Enum
from django.db import models
from django.db.models import Model, CharField, ImageField, CASCADE, ForeignKey, URLField, FileField
from taschoolassistant.users.models import User
from taschoolassistant.resources.managers import ResourceManager
from taschoolassistant.courses.models import CourseSession
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class TypeResource(Enum):
    LINK = 'Link'
    FILE =  'File'

class Resource(Model):
    link = URLField(blank=True, null=True)
    file = FileField(upload_to='resource-file/', blank=True, null=True)
    resource_type = CharField(
        max_length=50,
        choices=[(status.value, status.name) for status in TypeResource],
        default=TypeResource.FILE.value,
    )
    course_session = ForeignKey(CourseSession, on_delete=CASCADE)
    
    objects = ResourceManager()
