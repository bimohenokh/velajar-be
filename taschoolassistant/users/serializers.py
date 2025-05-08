from django.contrib.auth import get_user_model
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer, Serializer

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "nama_lengkap", "role"]


class RegisterInSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password","nama_lengkap", "role"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginInSerializer(Serializer):
    identifier = CharField()
    password = CharField(write_only=True)


class LoginOutSerializer(Serializer):
    refresh = CharField()
    access = CharField()
    user = UserSerializer()
