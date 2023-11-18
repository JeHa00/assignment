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


@pytest.mark.django_db
@pytest.mark.get_subtasks
def test_get_subtasks_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_subtasks: None,
):
    url = reverse("subtask_list_create")

    for page_number in range(1, 4):
        response = client.get(
            f"{url}?page={page_number}",
            headers=fake_authorization_header,
        )

        assert response.status_code == status.HTTP_200_OK

        assert "count" in response.data
        assert response.data["count"] == 30

        assert "previous" in response.data

        assert "next" in response.data

        assert "results" in response.data
        assert len(response.data["results"]) == 10


@pytest.mark.django_db
@pytest.mark.delete_a_subtask
def test_delete_subtask_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_subtask: Task,
):
    url = reverse("subtask", args=[fake_subtask.id])

    response = client.delete(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert SubTask.objects.filter(id=fake_subtask.id).exists() is False


@pytest.mark.django_db
@pytest.mark.delete_a_subtask
def test_delete_subtask_if_not_exist_task(
    client: APIClient(),
    fake_authorization_header: dict,
):
    not_exist_subtask_id = 1
    url = reverse("subtask", args=[not_exist_subtask_id])

    response = client.delete(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "해당되는 하위 업무를 찾을 수 없습니다."
    assert response.data["detail"].code == "SUBTASK_NOT_FOUND"


@pytest.mark.django_db
@pytest.mark.delete_a_subtask
def test_delete_subtask_if_forbidden(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_another_subtask: Task,
):
    url = reverse("subtask", args=[fake_another_subtask.id])

    response = client.delete(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        response.data["detail"] == "You do not have permission to perform this action."
    )
    assert response.data["detail"].code == "permission_denied"

    assert SubTask.objects.filter(id=fake_another_subtask.id).exists() is True
