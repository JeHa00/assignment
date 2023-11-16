from rest_framework.test import APIClient
from rest_framework import status
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
    user = User.objects.filter(id=1).last()

    assert response.status_code == status.HTTP_201_CREATED
    assert data_to_be_created["username"] == user.username
    assert data_to_be_created["password"] == user.password
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
