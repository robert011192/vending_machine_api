from unittest.mock import patch

from fastapi.security import HTTPBasicCredentials
from starlette import status
from starlette.testclient import TestClient

from main import app
from tests.mocks import return_user_info
from user.views import security


def override_dependency():
    return HTTPBasicCredentials(username="test", password="test")


app.dependency_overrides[security] = override_dependency


BUYER_ROLE = "buyer"
SELLER_ROLE = "seller"
USERNAME = "test"


def test_read_user_not_authenticated(test_client: TestClient):
    response = test_client.get(f"/user/{USERNAME}")
    with patch("core.utils.get_user", return_value=None):
        assert response.json() == {"detail": "Wrong credentials. Please try again"}
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_user(test_client: TestClient):
    user_actual_deposit = 50
    with patch(
        "core.utils.get_user",
        return_value=return_user_info(1, "test", user_actual_deposit, BUYER_ROLE),
    ):
        request = test_client.get(f"/user/{USERNAME}")
        assert request.status_code == status.HTTP_200_OK
        assert request.json()["username"] == "test"
