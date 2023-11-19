from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import pytest

# flake8: noqa
from subtasks.test.conftest import fake_subtasks

from common.utils import random_lower_string
from common.models import Base
from tasks.models import Task


@pytest.mark.django_db
@pytest.mark.get_a_task
def test_get_task_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_task: Task,
):
    url = reverse("task", args=[fake_task.id])

    response = client.get(url, headers=fake_authorization_header)
    assert response.status_code == status.HTTP_200_OK

    assert "id" in response.data
    assert response.data["id"] == fake_task.id

    assert "create_user" in response.data
    assert "username" in response.data["create_user"]
    assert "team" in response.data["create_user"]

    assert "title" in response.data

    assert "content" in response.data

    assert "team" in response.data

    assert "is_completed" in response.data
    assert response.data["is_completed"] is False

    assert "completed_at" in response.data
    assert response.data["completed_at"] is None


@pytest.mark.django_db
@pytest.mark.get_a_task
def test_get_task_if_not_exist_task(
    client: APIClient(),
    fake_authorization_header: dict,
):
    url = reverse("task", args=[1])

    response = client.get(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "해당되는 업무를 찾을 수 없습니다."
    assert response.data["detail"].code == "TASK_NOT_FOUND"


@pytest.mark.django_db
@pytest.mark.get_tasks
def test_get_tasks_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_tasks: None,
    fake_subtasks: None,
):
    url = reverse("task_list")

    for page_number in range(1, 6):
        response = client.get(
            f"{url}?page={page_number}",
            headers=fake_authorization_header,
        )
        assert response.status_code == status.HTTP_200_OK

        assert "count" in response.data

        # fake_tasks에서 30개가 생성되지만 인증 정보에 담긴 직원의 팀과 동일한 업무 소속은 15개.
        # fake_subtasks에서 인증 정보에 담긴 직원의 팀과 동일한 하위 업무 30개.
        assert response.data["count"] == 45

        assert "previous" in response.data

        assert "next" in response.data

        assert "results" in response.data

        # REST FRAMEWORK의 PAGE 사이즈가 10
        assert len(response.data["results"]) == 10 if page_number != 5 else 5


@pytest.mark.django_db
@pytest.mark.create_a_task
def test_create_task_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_user: dict,
):
    user = fake_user["user_object"]

    url = reverse("task_create")

    title_max_length = 100
    content_max_length = 1000

    data_to_be_created = {
        "title": f"{random_lower_string(k=title_max_length)}",
        "content": f"{random_lower_string(k=content_max_length)}",
        "team": user.team,
    }

    response = client.post(
        url,
        data_to_be_created,
        content_type="application/json",
        headers=fake_authorization_header,
    )
    assert response.status_code == status.HTTP_201_CREATED

    new_task = Task.objects.filter(id=1).last()

    assert new_task.create_user == user
    assert new_task.is_completed is False
    assert new_task.completed_at is None
    assert new_task.team == user.team
    assert new_task.title == data_to_be_created["title"]
    assert new_task.content == data_to_be_created["content"]


@pytest.mark.django_db
@pytest.mark.create_a_task
def test_create_task_if_bad_request(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_user: dict,
):
    url = reverse("task_create")

    title_max_length = 100
    content_max_length = 1000

    data_to_be_created = {
        "title": f"{random_lower_string(k=title_max_length)}",
        "content": f"{random_lower_string(k=content_max_length)}",
        "completed_at": False,
    }

    # 보낸 데이터에 team 정보가 없어서 발생
    response = client.post(
        url,
        data_to_be_created,
        content_type="application/json",
        headers=fake_authorization_header,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.update_a_task
def test_update_task_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_task: Task,
):
    url = reverse("task", args=[fake_task.id])

    previous_title = fake_task.title
    previous_content = fake_task.content
    previous_team = fake_task.team

    data_to_be_updated = {
        "title": "updated title",
        "content": "updated content",
        "team": Base.TeamChoices.DARAE,
    }

    response = client.put(
        url,
        data=data_to_be_updated,
        content_type="application/json",
        headers=fake_authorization_header,
    )

    assert response.status_code == status.HTTP_200_OK

    refreshed_task = Task.objects.filter(id=fake_task.id).last()

    assert fake_task.id == refreshed_task.id
    assert fake_task.create_user == refreshed_task.create_user
    assert fake_task.is_completed == refreshed_task.is_completed
    assert fake_task.completed_at == refreshed_task.completed_at
    assert fake_task.created_at == refreshed_task.created_at

    assert previous_title != refreshed_task.title
    assert previous_content != refreshed_task.content
    assert previous_team != refreshed_task.team
    assert fake_task.modified_at != refreshed_task.modified_at


@pytest.mark.django_db
@pytest.mark.update_a_task
def test_update_task_if_not_exist_task(
    client: APIClient(),
    fake_authorization_header: dict,
):
    not_exist_task_id = 1

    url = reverse("task", args=[not_exist_task_id])

    response = client.put(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "해당되는 업무를 찾을 수 없습니다."
    assert response.data["detail"].code == "TASK_NOT_FOUND"


@pytest.mark.django_db
@pytest.mark.update_a_task
def test_update_task_if_forbidden(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_another_task: Task,
):
    url = reverse("task", args=[fake_another_task.id])

    response = client.put(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        response.data["detail"] == "You do not have permission to perform this action."
    )
    assert response.data["detail"].code == "permission_denied"


@pytest.mark.django_db
@pytest.mark.mark_as_completion
def test_mark_as_completion_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_task: Task,
):
    url = reverse("task_completion", args=[fake_task.id])

    assert fake_task.is_completed is False

    response = client.patch(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "success to mark as completion"

    refreshed_task = Task.objects.filter(id=fake_task.id).last()

    assert refreshed_task.is_completed is True


@pytest.mark.django_db
@pytest.mark.mark_as_completion
def test_mark_as_completion_if_not_exist_task(
    client: APIClient(),
    fake_authorization_header: dict,
):
    not_exist_task_id = 1
    url = reverse("task_completion", args=[not_exist_task_id])

    response = client.patch(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "해당되는 업무를 찾을 수 없습니다."
    assert response.data["detail"].code == "TASK_NOT_FOUND"


@pytest.mark.django_db
@pytest.mark.mark_as_completion
def test_mark_as_completion_if_forbidden(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_another_task: Task,
):
    url = reverse("task_completion", args=[fake_another_task.id])

    assert fake_another_task.is_completed is False

    response = client.patch(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        response.data["detail"] == "You do not have permission to perform this action."
    )
    assert response.data["detail"].code == "permission_denied"

    assert fake_another_task.is_completed is False


@pytest.mark.django_db
@pytest.mark.delete_a_task
def test_delete_task_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_task: Task,
):
    url = reverse("task", args=[fake_task.id])

    response = client.delete(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert Task.objects.filter(id=fake_task.id).exists() is False


@pytest.mark.django_db
@pytest.mark.delete_a_task
def test_delete_task_if_not_exist_task(
    client: APIClient(),
    fake_authorization_header: dict,
):
    not_exist_task_id = 1
    url = reverse("task", args=[not_exist_task_id])

    response = client.delete(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "해당되는 업무를 찾을 수 없습니다."
    assert response.data["detail"].code == "TASK_NOT_FOUND"


@pytest.mark.django_db
@pytest.mark.delete_a_task
def test_delete_task_if_forbidden(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_another_task: Task,
):
    url = reverse("task", args=[fake_another_task.id])

    response = client.delete(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        response.data["detail"] == "You do not have permission to perform this action."
    )
    assert response.data["detail"].code == "permission_denied"

    assert Task.objects.filter(id=fake_another_task.id).exists() is True
