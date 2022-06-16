from sqlalchemy.orm import Session

from core import models
from core.models import User
from user.serializers import UserBase
from product.serializers import ProductCreate


def authenticate_user(
    db: Session,
    username: str,
    password: str,
    *,
    admin_requester=False,
    buyer_requester=False
):
    """
    Method used to authenticate a user
    :param db: database session
    :param username: the username
    :param password: the password
    :param admin_requester: if the user should be a admin
    :param buyer_requester: if the user should be a buyer
    :return: Bool
    """
    check_user = get_user(db, username)
    if check_user is None or check_user.password != password:
        return False, 401, "Wrong credentials. Please try again"

    if admin_requester:
        if check_user.role != "admin":
            return False, 400, "You should be admin to access this endpoint"

    if buyer_requester:
        if check_user.role != "buyer":
            return False, 400, "You should be a buyer to access this endpoint"

    return True, check_user


def get_user(db: Session, username: str):
    """
    Method used to get the user info by username
    :param db: db session
    :param username: username to get info for
    :return: user info
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    """
    Method used to get the user info by id
    :param db: db session
    :param user_id: userid to get info for
    :return: user info
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def remove_user(db: Session, username: str):
    """
    Remove user by username
    :param db: db session
    :param username: username to remove
    :return: removed user info
    """
    stmt = db.query(models.User).filter(models.User.username == username).delete()
    db.commit()
    return stmt


def create_user(db: Session, user: User):
    """
    Create user
    :param db: db session
    :param user: user info to use while creating it
    :return: the newly created user info
    """
    fake_hash_password = user.password + "notreallyhashed"
    db_user = models.User(
        username=user.username,
        password=fake_hash_password,
        deposit=user.deposit,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def update_user(db: Session, username: str, new_user_details: UserBase):
    """
    Update user by username
    :param db: db session
    :param username: username to update
    :param new_user_details: new user info to update
    :return: newly updated user info
    """
    db.query(models.User).filter(models.User.username == username).update(
        new_user_details.dict()
    )

    db.commit()

    return get_user(db, username)


def update_user_deposit(db: Session, username: str, deposit: int):
    """
    Update user deposit
    :param db: db session
    :param username: username to update
    :param deposit: deposit to add
    :return: updated user info
    """
    db.query(models.User).filter(models.User.username == username).update(
        {models.User.deposit: deposit}
    )

    db.commit()

    return get_user(db, username)


def create_user_product(db: Session, product: ProductCreate, seller_id: int):
    """
    Create a product for user
    :param db: db Session
    :param product: product info
    :param seller_id: seller to add product to
    :return: product info
    """
    db_item = models.Product(**product.dict(), seller_id=seller_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


def get_product_for_user(db: Session, product_name: str, seller_id: int):
    """
    Get a product for user by name
    :param db: db Session
    :param product_name: product info
    :param seller_id: seller to add product to
    :return: product info
    """
    return (
        db.query(models.Product)
        .filter(
            models.Product.product_name == product_name,
            models.Product.seller_id == seller_id,
        )
        .first()
    )


def get_product_by_id(db: Session, product_id: int):
    """
    Get product by id
    :param db: db Session
    :param product_id: product id to get info
    :return: product info
    """
    return (
        db.query(models.Product)
        .filter(
            models.Product.id == product_id,
        )
        .first()
    )


def get_all_products(db: Session, product_name: str):
    """
    Get all product by name
    :param db: db session
    :param product_name: product name to get
    :return: list of products
    """
    return (
        db.query(models.Product)
        .filter(models.Product.product_name == product_name)
        .all()
    )


def remove_product(db: Session, product_name: str, seller_id: int):
    """
    Remove a product by name for seller id
    :param db: db session
    :param product_name: product name to remove
    :param seller_id: seller id for the product
    :return: removed product info
    """
    stmt = (
        db.query(models.Product)
        .filter(
            models.Product.product_name == product_name,
            models.Product.seller_id == seller_id,
        )
        .delete()
    )
    db.commit()
    return stmt


def update_product(
    db: Session, product_name: str, seller_id: int, new_product_details: ProductCreate
):
    """
    Update a product for seller id by product name
    :param db: db session
    :param product_name: product name to update
    :param seller_id: seller id of the product
    :param new_product_details: new product info to update
    :return: newly updated product info
    """
    db.query(models.Product).filter(
        models.Product.product_name == product_name,
        models.Product.seller_id == seller_id,
    ).update(new_product_details.dict())

    db.commit()

    return get_product_for_user(db, product_name, seller_id)


def update_product_amount_available_by_id(
    db: Session, product_id: int, new_available_amount: int
):
    """
    Update product amount available
    :param db: db session
    :param product_id: product id
    :param new_available_amount: new available amount
    :return: new updated product info
    """
    db.query(models.Product).filter(models.Product.id == product_id).update(
        {models.Product.amount_available: new_available_amount}
    )

    db.commit()

    return get_product_by_id(db, product_id)
