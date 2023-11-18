from rest_framework import serializers

from accounts.serializers import UserSerializer
from subtasks.serializers import SubtaskSerializer
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    create_user = UserSerializer(read_only=True)
    subtasks = SubtaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "create_user",
            "subtasks",
            "team",
            "is_completed",
            "completed_at",
        ]
        read_only_fields = [
            "title",
            "content",
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
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
