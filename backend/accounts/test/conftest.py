from copy import deepcopy

from rest_framework.test import APIClient
from django.urls import reverse
import pytest

from common.utils import random_lower_string
from accounts.serializers import SignupSerializer
from accounts.models import User
from common.models import Base


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
        "team": Base.TeamChoices.DANBIE,
    }

    serializer = SignupSerializer(data_to_be_created)

    new_user = User.objects.create_user(**serializer.data)

    data_to_be_created.pop("team")

    return {"user_object": new_user, "login_data": deepcopy(data_to_be_created)}


@pytest.fixture(scope="function")
@pytest.mark.django_db
def fake_authorization_header(
    client: APIClient(),
    fake_user: dict,
) -> dict:
    login_data = fake_user["login_data"]

    response = client.post(reverse("login"), login_data)

    access_token = response.data["token_information"]["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
@pytest.mark.django_db
def fake_another_user() -> dict:
    """fake_user와 그룹이 다른 테스트용 유저를 1명 생성한다.

    Returns:
        dict: 새로 생성된 User 객체 와 로그인 정보를 반환
    """
    data_to_be_created = {
        "username": f"user-{random_lower_string(k=10)}",
        "password": random_lower_string(k=10),
        "team": Base.TeamChoices.CHEOLLO,
    }

    serializer = SignupSerializer(data_to_be_created)

    new_user = User.objects.create_user(**serializer.data)

    data_to_be_created.pop("team")

    return {"user_object": new_user, "login_data": deepcopy(data_to_be_created)}
