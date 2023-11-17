from rest_framework import serializers

from accounts.serializers import UserSerializer
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    create_user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "create_user",
            "title",
            "content",
            "team",
            "is_completed",
            "completed_at",
        ]
