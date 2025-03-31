from rest_framework import serializers
from rest_framework.fields import CharField, IntegerField, JSONField
from rest_framework.serializers import Serializer
from typing_extensions import TypeVar

T = TypeVar("T", bound=serializers.Serializer)


class StandardOutSerializer(Serializer):
    status = IntegerField(default=200)
    message = CharField(default="[Doing] successful")
    data = JSONField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure `data` is properly serialized
        data = instance.get("data")
        if isinstance(data, serializers.BaseSerializer):
            representation["data"] = data.data  # Convert serializer to dictionary
        else:
            representation["data"] = data  # Keep as-is (list, dict, string, etc.)

        return representation

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
    errors = JSONField(default=dict)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Normalize 'errors' so it is always a dictionary
        errors = instance.get("errors", {})

        if isinstance(errors, str):
            representation["errors"] = {"detail": [errors]}  # Convert string to list inside a dictionary
        elif isinstance(errors, list):
            representation["errors"] = {"detail": errors}  # Wrap list inside a dictionary
        else:
            representation["errors"] = errors  # Keep as-is if already a dictionary

        return representation

    @classmethod
    def open_api_wrap(cls, the_status=400, the_message="An error occurred", the_error=None):
        class WrappedStandardErrorOutSerializer(cls):
            status = IntegerField(default=the_status)
            message = CharField(default=the_message)
            errors = JSONField(default=the_error or {})

            class Meta:
                ref_name = f"StandardErrorOut{the_status}"

        return WrappedStandardErrorOutSerializer
