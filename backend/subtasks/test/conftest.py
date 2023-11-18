import pytest

# flake8: noqa
from accounts.test.conftest import (
    fake_user,
    fake_another_user,
    fake_authorization_header,
)

# flake8: noqa
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
def fake_subtasks(
    fake_task: Task,
    fake_another_task: Task,
) -> None:
    """fake_task의 하위업무 subtask를 테스트용으로 30개 생성한다.
        생성된 하위 업무는 모두  DANBIE 팀에 속한다.
        하위 업무 15개의 상위 업무 담당 팀은 동일하게 DANBIE,
        나머지 15개의 상위 업무 담당 팀은 CHELLO 로 다르다.

    Args:
        fake_task (Task): 테스트용 업무 1개를 생성하는 fixture

    """
    total_count = 30

    for id in range(total_count):
        data_to_be_created = {"team": Base.TeamChoices.DANBIE}

        serializer = SubtaskSerializer(data_to_be_created)

        if id < 15:
            SubTask.objects.create(
                task=fake_task,  # DANBIE team
                **serializer.data,
            )
        else:
            SubTask.objects.create(
                task=fake_another_task,  # CHELLO team
                **serializer.data,
            )
