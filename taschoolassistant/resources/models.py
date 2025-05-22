from enum import Enum
from django.db import models
from django.db.models import (
    Model,
    CharField,
    ImageField,
    CASCADE,
    ForeignKey,
    URLField,
    FileField,
    TextChoices,
    CheckConstraint,
    Q,
)
from taschoolassistant.users.models import User
from taschoolassistant.resources.managers import ResourceManager
from taschoolassistant.courses.models import CourseSession


class ResourceType(TextChoices):
    LINK = 'Link'
    FILE =  'File'

class Resource(Model):
    # FIXME not working
    # class Meta:
    #     constraints = [
    #         CheckConstraint(
    #             check=(
    #                 (Q(link__isnull=False) & Q(file__isnull=True))
    #                 | (Q(link__isnull=True) & Q(file__isnull=False))
    #             ),
    #             name="link_xor_file",
    #         )
    #     ]

    course_session = ForeignKey(CourseSession, on_delete=CASCADE)
    link = URLField(blank=True, null=True)
    file = FileField(upload_to='resource-file/', blank=True, null=True)

    objects = ResourceManager()

    @property
    def resource_type(self):
        if self.link:
            return ResourceType.LINK
        elif self.file:
            return ResourceType.FILE
        else:
            return None
    

