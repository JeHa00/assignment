from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import pytest

from common.utils import random_lower_string
from common.models import Base
from tasks.models import Task
from subtasks.serializers import SubtaskSerializer
from subtasks.models import SubTask


@pytest.mark.django_db
@pytest.mark.get_a_subtask
def test_get_subtask_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_task: Task,
    fake_subtask: SubTask,
):
    url = reverse("subtask", args=[fake_subtask.id])

    response = client.get(url, headers=fake_authorization_header)
    assert response.status_code == status.HTTP_200_OK

    assert "id" in response.data
    assert response.data["id"] == fake_subtask.id

    assert "task" in response.data
    assert response.data["task"]["id"] == fake_task.id

    assert "team" in response.data

    assert "is_completed" in response.data
    assert response.data["is_completed"] is False

    assert "completed_at" in response.data
    assert response.data["completed_at"] is None


@pytest.mark.django_db
@pytest.mark.get_a_subtask
def test_get_subtask_if_not_exist_task(
    client: APIClient(),
    fake_authorization_header: dict,
):
    url = reverse("subtask", args=[1])

    response = client.get(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "해당되는 하위 업무를 찾을 수 없습니다."
    assert response.data["detail"].code == "SUBTASK_NOT_FOUND"
