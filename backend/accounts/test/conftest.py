from copy import deepcopy

import pytest

from common.utils import random_lower_string
from accounts.serializers import SignupSerializer
from accounts.models import User


@pytest.fixture(scope="function")
@pytest.mark.django_db
def fake_user() -> dict:
    """테스트용 유저를 1명 생성한다.

    Returns:
        dict: 새로 생성된 User 객체 와 로그인 정보를 반환
    """
    data_to_be_created = {
        "username": f"user-{random_lower_string(k=10)}",
        "password": random_lower_string(k=10),
        "team": User.TeamChoices.DANBIE,
    }

    serializer = SignupSerializer(data_to_be_created)

    new_user = User.objects.create_user(**serializer.data)

    data_to_be_created.pop("team")

    return {"user_object": new_user, "login_data": deepcopy(data_to_be_created)}
