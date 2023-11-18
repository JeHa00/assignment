from django.utils import timezone
import pytest

from tasks.models import Task
from subtasks.models import SubTask


@pytest.mark.django_db
def test_signal_on_task_completion(
    fake_task: Task,
    fake_subtasks: None,
):
    assert fake_task.is_completed is False
    assert fake_task.completed_at is None

    for id in range(1, 31):
        selected_subtask = SubTask.objects.filter(id=id).last()

        selected_subtask.is_completed = True
        selected_subtask.completed_at = timezone.localtime(timezone.now())
        selected_subtask.save()

    refreshed_task = Task.objects.filter(id=fake_task.id).last()

    assert refreshed_task.is_completed is True
    assert not refreshed_task.completed_at is True
