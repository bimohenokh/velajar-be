from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import StudentProfile, TeacherProfile
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "nama_lengkap", "email", "password"]

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        nama_lengkap = validated_data.pop('nama_lengkap', None)
        password = validated_data.pop('password', None)
        
        if password:
            instance.password = make_password(password)

        instance.nama_lengkap = nama_lengkap
        return super().update(instance, validated_data)


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = StudentProfile
        fields = ["id", "user", "image_profile", "dateOfBirth", "school", "student_class"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                raise serializers.ValidationError(user_serializer.errors)
        return super().update(instance, validated_data)


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = TeacherProfile
        fields = ["id", "user", "image_profile", "dateOfBirth", "school"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                raise serializers.ValidationError(user_serializer.errors)
        return super().update(instance, validated_data)
    

class StudentPostProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        read_only_fields = ["user"]

    def create(self, validated_data):
        user = self.context.get("user")
        return StudentProfile.objects.create(user=user, **validated_data)


class TeacherPostProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        read_only_fields = ["user"]

    def create(self, validated_data):
        user = self.context.get("user")
        return TeacherProfile.objects.create(user=user, **validated_data)
