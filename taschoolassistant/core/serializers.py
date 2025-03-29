from rest_framework import serializers
from rest_framework.fields import CharField, IntegerField, SerializerMethodField, DictField
from rest_framework.serializers import Serializer
from typing_extensions import Generic, TypeVar

T = TypeVar("T", bound=serializers.Serializer)


class StandardOutSerializer(Serializer, Generic[T]):
    status = IntegerField(default=200)
    message = CharField(default="[Doing] successful")
    data = SerializerMethodField()

    def get_data(self, obj):
        # Ensure the nested serializer is properly instantiated and serialized
        if isinstance(obj["data"], serializers.Serializer):
            return obj["data"].data
        return obj["data"]

    @classmethod
    def open_api_wrap(cls, serializer: T, the_status=200, the_message="[Doing] successful"):
        class WrappedStandardOutSerializer(cls):
            status = IntegerField(default=the_status)
            message = CharField(default=the_message)
            data = serializer()

            class Meta:
                ref_name = f"StandardOut{serializer.__name__}"

        return WrappedStandardOutSerializer


class StandardErrorOutSerializer(Serializer):
    status = IntegerField(default=400)
    message = CharField(default="An error occurred")
    errors = DictField(default={})

    @classmethod
    def open_api_wrap(cls, the_status=400, the_message="An error occurred", the_error=None):
        class WrappedStandardErrorOutSerializer(cls):
            status = IntegerField(default=the_status)
            message = CharField(default=the_message)
            errors = DictField(default=the_error or {})

            class Meta:
                ref_name = f"StandardErrorOut{the_status}"

        return WrappedStandardErrorOutSerializer
