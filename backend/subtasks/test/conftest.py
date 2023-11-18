import pytest

from common.utils import random_lower_string
from accounts.test.conftest import (
    fake_user,
    fake_another_user,
    fake_authorization_header,
)

from tasks.test.conftest import (
    fake_task,
    fake_another_task,
    fake_tasks,
)

from subtasks.serializers import SubtaskSerializer
from common.models import Base
from tasks.models import Task
from subtasks.models import SubTask


@pytest.fixture(scope="function")
@pytest.mark.django_db
def fake_subtask(
    fake_task: Task,
) -> SubTask:
    """테스트용 subtask를 1개 생성한다.

    Args:
        fake_user (dict): 테스트용 업무 1개를 생성하는 fixture

    Returns:
        Subtask: 새로 생성된 Subtask instance를 반환
    """
    data_to_be_created = {"team": Base.TeamChoices.DANBIE}

    serializer = SubtaskSerializer(data_to_be_created)

    new_task = SubTask.objects.create(
        task=fake_task,
        **serializer.data,
    )

    return new_task


@pytest.fixture(scope="function")
@pytest.mark.django_db
def fake_another_subtask(fake_task: Task) -> SubTask:
    """테스트용 subtask를 1개 생성한다.

    Args:
        fake_task (dict): 테스트용 업무 1개를 생성하는 fixture

    Returns:
        SubTask: 새로 생성된 Subtask instance를 반환
    """
    data_to_be_created = {"team": Base.TeamChoices.CHEOLLO}

    serializer = SubtaskSerializer(data_to_be_created)

    new_task = SubTask.objects.create(
        task=fake_task,
        **serializer.data,
    )

    return new_task


@pytest.fixture(scope="function")
@pytest.mark.django_db
def fake_subtasks(fake_task: dict) -> None:
    """fake_task의 하위업무 subtask를 테스트용으로 10개 생성한다.

    Args:
        fake_task (dict): 테스트용 업무 1개를 생성하는 fixture

    """
    total_count = 30

    for _ in range(total_count):
        data_to_be_created = {"team": Base.TeamChoices.DANBIE}

        serializer = SubtaskSerializer(data_to_be_created)

        SubTask.objects.create(
            task=fake_task,
            **serializer.data,
        )
