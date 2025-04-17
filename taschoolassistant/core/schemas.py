from typing_extensions import TypeVar

from rest_framework.fields import IntegerField, CharField, JSONField
from rest_framework.serializers import Serializer

from taschoolassistant.core.serializers import StandardOutSerializer, StandardErrorOutSerializer

T = TypeVar("T", bound=Serializer)


def open_api_wrap(serializer: T, the_status=200, the_message="[Doing] successful"):
    class WrappedStandardOutSerializer(StandardOutSerializer):
        status = IntegerField(default=the_status)
        message = CharField(default=the_message)
        data = serializer()

        class Meta:
            ref_name = f"StandardOut{serializer.__name__}"

    return WrappedStandardOutSerializer


def error_open_api_wrap(the_status=400, the_message="An error occurred", the_error=None):
    class WrappedStandardOutSerializer(StandardErrorOutSerializer):
        status = IntegerField(default=the_status)
        message = CharField(default=the_message)
        errors = JSONField(default=the_error or {})

        class Meta:
            ref_name = f"StandardErrorOut{the_status}"

    return WrappedStandardOutSerializer

