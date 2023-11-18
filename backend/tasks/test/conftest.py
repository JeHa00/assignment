import pytest

from common.utils import random_lower_string

# flake8: noqa
from accounts.test.conftest import (
    fake_user,
    fake_another_user,
    fake_authorization_header,
)

from tasks.serializers import TaskSerializer
from common.models import Base
from tasks.models import Task


@pytest.fixture(scope="function")
@pytest.mark.django_db
def fake_task(fake_user: dict) -> Task:
    """테스트용 task를 1개 생성한다.

    Args:
        fake_user (dict): 테스트용 유저 1명을 생성하는 fixture

    Returns:
        Task: 새로 생성된 Task instance를 반환
    """
    data_to_be_created = {
        "title": f"{random_lower_string(k=100)}",
        "content": f"{random_lower_string(k=1000)}",
        "team": Base.TeamChoices.DANBIE,
    }

    serializer = TaskSerializer(data_to_be_created)

    new_task = Task.objects.create(
        create_user=fake_user["user_object"],
        **serializer.data,
    )

    return new_task


@pytest.fixture(scope="function")
@pytest.mark.django_db
def fake_another_task(fake_another_user: dict) -> Task:
    """테스트용 task를 1개 생성한다.

    Args:
        fake_user (dict): 테스트용 유저 1명을 생성하는 fixture

    Returns:
        Task: 새로 생성된 Task instance를 반환
    """
    data_to_be_created = {
        "title": f"{random_lower_string(k=100)}",
        "content": f"{random_lower_string(k=1000)}",
        "team": Base.TeamChoices.CHEOLLO,
    }

    serializer = TaskSerializer(data_to_be_created)

    new_task = Task.objects.create(
        create_user=fake_another_user["user_object"],
        **serializer.data,
    )

    return new_task


@pytest.fixture(scope="function")
@pytest.mark.django_db
def fake_tasks(fake_user: dict) -> None:
    """fake_user가 생성자인 테스트용 task를 10개 생성한다.

    Args:
        fake_user (dict): 테스트용 유저 1명을 생성하는 fixture

    """
    user = fake_user.get("user_object")

    total_count = 30

    for id in range(total_count):
        data_to_be_created = {
            "title": f"{random_lower_string(k=100)}",
            "content": f"{random_lower_string(k=1000)}",
        }
        if id < 15:
            data_to_be_created["team"] = Base.TeamChoices.DANBIE
        else:
            data_to_be_created["team"] = Base.TeamChoices.BLABLA

        serializer = TaskSerializer(data_to_be_created)

        Task.objects.create(
            create_user=user,
            **serializer.data,
        )
