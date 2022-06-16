from unittest.mock import patch

from fastapi.security import HTTPBasicCredentials
from starlette import status
from starlette.testclient import TestClient

from main import app
from tests.mocks import return_user_info, return_get_product_by_id
from product.views import security


def override_dependency():
    return HTTPBasicCredentials(username="test", password="test")


app.dependency_overrides[security] = override_dependency


BUYER_ROLE = "buyer"
SELLER_ROLE = "seller"


def return_product_and_amount(product_id: int, amount: int):
    return {"product_id": product_id, "amount": amount}


def test_buy_product_not_authenticated(test_client: TestClient):
    response = test_client.get("/buy", params=return_product_and_amount(1, 2))
    with patch("core.utils.get_user", return_value=None):
        assert response.json() == {"detail": "Wrong credentials. Please try again"}
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_buy_product_not_buyer(test_client: TestClient):
    user_actual_deposit = 50
    with patch(
        "core.utils.get_user",
        return_value=return_user_info(1, "test", user_actual_deposit, SELLER_ROLE),
    ):
        request = test_client.get("/buy", params=return_product_and_amount(1, 2))
        assert (
            request.json()["detail"] == "You should be a buyer to access this endpoint"
        )
        assert request.status_code == status.HTTP_400_BAD_REQUEST


def test_buy_product_zero_deposit(test_client: TestClient):
    user_actual_deposit = 0
    with patch(
        "core.utils.get_user",
        return_value=return_user_info(1, "test", user_actual_deposit, BUYER_ROLE),
    ):
        with patch(
            "product.views.utils.get_product_by_id",
            return_value=return_get_product_by_id("Cola", 1, 55, 1),
        ):
            request = test_client.get("/buy", params=return_product_and_amount(1, 2))
            assert (
                request.json()["detail"]
                == "Your balance is 0. Please refill your account"
            )
            assert request.status_code == status.HTTP_400_BAD_REQUEST


def test_buy_product_not_enough_deposit(test_client: TestClient):
    user_actual_deposit = 60
    with patch(
        "core.utils.get_user",
        return_value=return_user_info(1, "test", user_actual_deposit, BUYER_ROLE),
    ):
        with patch(
            "product.views.utils.get_product_by_id",
            return_value=return_get_product_by_id("Cola", 1, 55, 1),
        ):
            request = test_client.get("/buy", params=return_product_and_amount(1, 2))
            assert request.json()["detail"] == "You can buy: 1 pcs!"
            assert request.status_code == status.HTTP_400_BAD_REQUEST


def test_buy_product_no_pcs_to_buy(test_client: TestClient):
    user_actual_deposit = 50
    with patch(
        "core.utils.get_user",
        return_value=return_user_info(1, "test", user_actual_deposit, BUYER_ROLE),
    ):
        with patch(
            "product.views.utils.get_product_by_id",
            return_value=return_get_product_by_id("Cola", 1, 55, 1),
        ):
            request = test_client.get("/buy", params=return_product_and_amount(1, 2))
            assert (
                request.json()["detail"]
                == "You can buy no pcs. Try deposit or chose another product!"
            )
            assert request.status_code == status.HTTP_400_BAD_REQUEST


def test_buy_product_no_amount_available(test_client: TestClient):
    user_actual_deposit = 150
    with patch(
        "core.utils.get_user",
        return_value=return_user_info(1, "test", user_actual_deposit, BUYER_ROLE),
    ):
        with patch(
            "product.views.utils.get_product_by_id",
            return_value=return_get_product_by_id("Cola", 0, 55, 1),
        ):
            request = test_client.get("/buy", params=return_product_and_amount(1, 2))
            assert (
                request.json()["detail"]
                == "No product amount available. Please try another product"
            )
            assert request.status_code == status.HTTP_400_BAD_REQUEST


def test_buy_product_only_one_product_available(test_client: TestClient):
    user_actual_deposit = 150
    with patch(
        "core.utils.get_user",
        return_value=return_user_info(1, "test", user_actual_deposit, BUYER_ROLE),
    ):
        with patch(
            "product.views.utils.get_product_by_id",
            return_value=return_get_product_by_id("Cola", 1, 55, 1),
        ):
            request = test_client.get("/buy", params=return_product_and_amount(1, 2))
            assert request.json()["detail"] == "Only 1 pcs available"
            assert request.status_code == status.HTTP_400_BAD_REQUEST
