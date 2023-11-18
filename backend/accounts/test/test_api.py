from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.urls import reverse
import pytest

from common.utils import random_lower_string
from accounts.models import User


@pytest.mark.django_db
@pytest.mark.signup
def test_signup_if_success(
    client: APIClient(),
):
    data_to_be_created = {
        "username": f"user-{random_lower_string(k=10)}",
        "password": random_lower_string(k=10),
        "team": User.TeamChoices.DANBIE,
    }

    url = reverse("signup")

    response = client.post(url, data_to_be_created)

    first_user_id = 1

    user = User.objects.filter(id=first_user_id).last()

    raw_password = data_to_be_created["password"]

    assert response.status_code == status.HTTP_201_CREATED
    assert data_to_be_created["username"] == user.username
    assert check_password(raw_password, user.password) is True
    assert data_to_be_created["team"] == user.team


@pytest.mark.django_db
@pytest.mark.signup
def test_signup_if_not_success(
    client: APIClient(),
):
    data_to_be_created = {"username": f"user-{random_lower_string(k=10)}"}

    url = reverse("signup")

    response = client.post(url, data_to_be_created)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.login
def test_login_if_success(client: APIClient(), fake_user: dict):
    user = fake_user["user_object"]
    login_data = fake_user["login_data"]

    url = reverse("login")

    response = client.post(url, login_data)

    assert response.status_code == status.HTTP_200_OK

    user_data = response.data["user_data"]

    assert "token" in response.data
    token_data = response.data["token"]

    assert "user_id" in user_data
    assert user_data["user_id"] == user.id

    assert "username" in user_data
    assert user_data["username"] == user.username

    assert "message" in response.data
    assert response.data["message"] == "LOGIN_SUCCESS"

    assert "access_token" in token_data
    assert "refresh_token" in token_data


@pytest.mark.django_db
@pytest.mark.login
def test_login_if_not_registered_user(
    client: APIClient(),
):
    login_data = {"username": "abcddefdef", "password": "abcdefd"}

    url = reverse("login")

    response = client.post(url, login_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "해당되는 유저를 찾을 수 없습니다."
    assert response.data["detail"].code == "USER_NOT_FOUND"


@pytest.mark.django_db
@pytest.mark.login
def test_login_if_wrong_password(
    client: APIClient(),
    fake_user: dict,
):
    login_data = fake_user["login_data"]

    login_data["password"] = "abcdefg"

    url = reverse("login")

    response = client.post(url, login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "입력한 비밀번호가 기존 비밀번호와 일치하지 않습니다."
    assert response.data["detail"].code == "WRONG_PASSWORD"


@pytest.mark.django_db
@pytest.mark.logout
def test_logout_if_success(
    client: APIClient(),
    fake_user: dict,
):
    # 로그인하여 token 정보 얻기
    login_data = fake_user["login_data"]

    login_url = reverse("login")

    response = client.post(login_url, login_data)

    access_token = response.data["token"]["access_token"]

    # 로그아웃 후, 토큰 정보 삭제 확인
    logout_url = reverse("logout")

    header = {"Authorization": f"Bearer {access_token}"}

    response = client.delete(logout_url, headers=header)

    assert response.status_code == status.HTTP_202_ACCEPTED
