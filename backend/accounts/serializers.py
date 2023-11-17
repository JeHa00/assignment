from django.contrib.auth import password_validation
from rest_framework import serializers

from accounts.models import User


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "team"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get("username"),
            password=validated_data.get("password"),
            team=validated_data.get("team"),
        )
        return user

    def validate_password(self, data):
        password_validation.validate_password(data, self.instance)
        return data


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "team"]
