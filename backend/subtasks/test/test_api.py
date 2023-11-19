from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from django.urls import reverse
import pytest

from common.models import Base
from tasks.models import Task
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

    assert "team" in response.data
    assert response.data["team"] == Base.TeamChoices.DANBIE

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
    url = reverse("subtask_list")

    for page_number in range(1, 4):
        response = client.get(
            f"{url}?page={page_number}",
            headers=fake_authorization_header,
        )
        assert response.status_code == status.HTTP_200_OK

        assert "count" in response.data

        # fake_subtasks fixture에서 생성한 subtask 총 수 30개
        assert response.data["count"] == 30

        assert "previous" in response.data

        assert "next" in response.data

        assert "results" in response.data

        # REST FRAMEWORK PAGE SIZE: 10
        assert len(response.data["results"]) == 10


@pytest.mark.django_db
@pytest.mark.create_a_subtask
def test_create_subtask_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_task: Task,
):
    data_to_be_created = {"team": Base.TeamChoices.DANBIE}

    url = reverse("subtask_create", args=[fake_task.id])

    response = client.post(
        url,
        data_to_be_created,
        headers=fake_authorization_header,
    )
    assert response.status_code == status.HTTP_201_CREATED

    assert SubTask.objects.filter(id=1).exists() is True

    assert "id" in response.data
    assert response.data["id"] == fake_task.id

    assert "team" in response.data
    assert response.data["team"] == Base.TeamChoices.DANBIE

    assert "is_completed" in response.data
    assert response.data["is_completed"] is False

    assert "completed_at" in response.data
    assert response.data["completed_at"] is None


@pytest.mark.django_db
@pytest.mark.create_a_subtask
def test_create_subtask_if_not_found_task(
    client: APIClient(),
    fake_authorization_header: dict,
):
    data_to_be_created = {"team": Base.TeamChoices.DANBIE}

    not_existed_task_id = 1

    url = reverse("subtask_create", args=[not_existed_task_id])

    response = client.post(
        url,
        data_to_be_created,
        headers=fake_authorization_header,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.update_a_subtask
def test_update_subtask_if_success(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_subtask: SubTask,
):
    url = reverse("subtask", args=[fake_subtask.id])

    assert fake_subtask.team == Base.TeamChoices.DANBIE

    data_to_be_updated = {"team": Base.TeamChoices.BLABLA}

    response = client.patch(
        url,
        data_to_be_updated,
        headers=fake_authorization_header,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK

    refreshed_subtask = SubTask.objects.filter(id=fake_subtask.id).last()

    assert refreshed_subtask.team == Base.TeamChoices.BLABLA


@pytest.mark.django_db
@pytest.mark.update_a_subtask
def test_update_subtask_if_not_found(
    client: APIClient(),
    fake_authorization_header: dict,
):
    not_existed_subtask_id = 1

    url = reverse("subtask", args=[not_existed_subtask_id])

    data_to_be_updated = {"team": Base.TeamChoices.DANGI}

    response = client.patch(
        url,
        data_to_be_updated,
        headers=fake_authorization_header,
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.update_a_subtask
def test_update_subtask_if_bad_request(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_subtask: SubTask,
):
    url = reverse("subtask", args=[fake_subtask.id])

    data_to_be_updated = {"team": None}

    response = client.patch(
        url,
        data_to_be_updated,
        headers=fake_authorization_header,
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["team"].pop() == "This field may not be null."


@pytest.mark.django_db
@pytest.mark.update_a_subtask
def test_update_subtask_if_forbidden(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_another_subtask: SubTask,
):
    url = reverse("subtask", args=[fake_another_subtask.id])

    data_to_be_updated = {"team": None}

    response = client.patch(
        url,
        data_to_be_updated,
        headers=fake_authorization_header,
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        response.data["detail"] == "You do not have permission to perform this action."
    )
    assert response.data["detail"].code == "permission_denied"


@pytest.mark.django_db
@pytest.mark.update_a_subtask
def test_update_subtask_if_success_by_put_method(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_subtask: SubTask,
):
    url = reverse("subtask", args=[fake_subtask.id])

    assert fake_subtask.team == Base.TeamChoices.DANBIE

    data_to_be_updated = {
        "team": Base.TeamChoices.BLABLA,
        "is_completed": True,
        "completed_at": timezone.localtime(timezone.now()),
    }

    response = client.put(
        url,
        data_to_be_updated,
        headers=fake_authorization_header,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK

    refreshed_subtask = SubTask.objects.filter(id=fake_subtask.id).last()

    assert refreshed_subtask.team == Base.TeamChoices.BLABLA
    assert refreshed_subtask.is_completed is True
    assert refreshed_subtask.completed_at is not None


@pytest.mark.django_db
@pytest.mark.update_a_subtask
def test_update_subtask_if_not_found_by_put_method(
    client: APIClient(),
    fake_authorization_header: dict,
):
    not_existed_subtask_id = 1

    url = reverse("subtask", args=[not_existed_subtask_id])

    data_to_be_updated = {
        "team": Base.TeamChoices.BLABLA,
        "is_completed": True,
        "completed_at": timezone.localtime(timezone.now()),
    }

    response = client.put(
        url,
        data_to_be_updated,
        headers=fake_authorization_header,
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.update_a_subtask
def test_update_subtask_if_bad_request_by_put_method(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_subtask: SubTask,
):
    url = reverse("subtask", args=[fake_subtask.id])

    data_to_be_updated = {
        "team": None,
        "is_completed": True,
        "completed_at": timezone.localtime(timezone.now()),
    }

    response = client.put(
        url,
        data_to_be_updated,
        headers=fake_authorization_header,
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["team"].pop() == "This field may not be null."


@pytest.mark.django_db
@pytest.mark.update_a_subtask
def test_update_subtask_if_forbidden_by_put_method(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_another_subtask: SubTask,
):
    url = reverse("subtask", args=[fake_another_subtask.id])

    data_to_be_updated = {
        "team": Base.TeamChoices.BLABLA,
        "is_completed": True,
        "completed_at": timezone.localtime(timezone.now()),
    }

    response = client.put(
        url,
        data_to_be_updated,
        headers=fake_authorization_header,
        content_type="application/json",
    )
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
    fake_subtask: Task,
):
    url = reverse("subtask_completion", args=[fake_subtask.id])

    assert fake_subtask.is_completed is False

    response = client.patch(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "success to mark as completion"

    refreshed_task = SubTask.objects.filter(id=fake_subtask.id).last()

    assert refreshed_task.is_completed is True


@pytest.mark.django_db
@pytest.mark.mark_as_completion
def test_mark_as_completion_if_not_exist_task(
    client: APIClient(),
    fake_authorization_header: dict,
):
    not_exist_subtask_id = 1
    url = reverse("subtask_completion", args=[not_exist_subtask_id])

    response = client.patch(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "해당되는 하위 업무를 찾을 수 없습니다."
    assert response.data["detail"].code == "SUBTASK_NOT_FOUND"


@pytest.mark.django_db
@pytest.mark.mark_as_completion
def test_mark_as_completion_if_forbidden(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_another_subtask: Task,
):
    url = reverse("subtask_completion", args=[fake_another_subtask.id])

    assert fake_another_subtask.is_completed is False

    response = client.patch(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        response.data["detail"] == "You do not have permission to perform this action."
    )
    assert response.data["detail"].code == "permission_denied"

    assert fake_another_subtask.is_completed is False


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


@pytest.mark.django_db
@pytest.mark.delete_a_subtask
def test_delete_subtask_if_completed_subtask(
    client: APIClient(),
    fake_authorization_header: dict,
    fake_subtask: Task,
):
    # 완료 처리 하기
    url = reverse("subtask_completion", args=[fake_subtask.id])

    assert fake_subtask.is_completed is False

    response = client.patch(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "success to mark as completion"

    refreshed_task = SubTask.objects.filter(id=fake_subtask.id).last()

    assert refreshed_task.is_completed is True

    # 완료 처리된 하위 업무 삭제 시도
    url = reverse("subtask", args=[fake_subtask.id])

    response = client.delete(url, headers=fake_authorization_header)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "이미 완료된 하위업무이기 때문에 삭제할 수 없습니다."
    assert response.data["detail"].code == "COMPLETED_SUBTASK_ERROR"
