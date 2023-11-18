from rest_framework import serializers

from tasks.serializers import TaskSerializer
from subtasks.models import SubTask


class SubtaskSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = SubTask
        fields = [
            "id",
            "task",
            "team",
            "is_completed",
            "completed_at",
        ]
