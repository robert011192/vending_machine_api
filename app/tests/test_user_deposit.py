from unittest.mock import patch

from fastapi.security import HTTPBasicCredentials
from starlette import status
from starlette.testclient import TestClient

from main import app
from tests.mocks import get_mock_coin_value, return_user_info
from user.views import security


def override_dependency():
    return HTTPBasicCredentials(username="test", password="test")


app.dependency_overrides[security] = override_dependency


BUYER_ROLE = "buyer"
SELLER_ROLE = "seller"


def test_user_deposit_coin_not_authenticated(test_client: TestClient):
    response = test_client.put("/deposit", json=get_mock_coin_value(5))
    with patch("core.utils.get_user", return_value=None):
        assert response.json() == {"detail": "Wrong credentials. Please try again"}
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_buyer_user_deposit_coin(test_client: TestClient):
    user_actual_deposit = 50
    add_coin_to_user = 5
    total_coins = user_actual_deposit + add_coin_to_user
    with patch(
        "core.utils.get_user",
        return_value=return_user_info(1, "test", user_actual_deposit, BUYER_ROLE),
    ):
        with patch("user.views.utils.update_user_deposit") as deposit_mock:
            test_client.put("/deposit", json=get_mock_coin_value(5))
            assert deposit_mock.call_args[0][1] == "test"
            assert deposit_mock.call_args[0][2] == total_coins


def test_other_user_deposit_coin(test_client: TestClient):
    user_actual_deposit = 50
    with patch(
        "core.utils.get_user",
        return_value=return_user_info(1, "test", user_actual_deposit, SELLER_ROLE),
    ):
        request = test_client.put("/deposit", json=get_mock_coin_value(5))
        assert request.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            request.json()["detail"] == "You have to be a buyer to be able to deposit"
        )
