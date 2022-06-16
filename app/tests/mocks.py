from typing import Dict, Any

from core.models import User, Product


def get_mock_coin_value(coin_value: int) -> Dict[str, Any]:
    return {"coin_value": coin_value}


def get_buy_product(product_id: int, amount: int) -> Dict[str, Any]:
    return {"product_id": product_id, "amount": amount}


def return_get_product_by_id(
    product_name: str, amount_available: int, cost: int, seller_id: int
) -> Dict[str, Any]:
    return Product(
        product_name=product_name,
        amount_available=amount_available,
        cost=cost,
        seller_id=seller_id,
    )


def return_user_info(id: int, username: str, deposit: int, role: str):
    return User(
        id=id,
        username=username,
        password="test",
        deposit=deposit,
        role=role,
    )
