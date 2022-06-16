from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from core import utils, models
from core.database import engine, SessionLocal
from product.serializers import ProductCreate, Product

models.Base.metadata.create_all(bind=engine)

router = APIRouter()
security = HTTPBasic()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/product", response_model=Product)
def create_product_for_user(
    product: ProductCreate,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
):
    """
    Create a product for the user
    :param product: product info
    :param db: database session
    :param credentials: user credentials
    :return: the created product
    """
    # first check if the credentials are ok
    auth_user = utils.authenticate_user(db, credentials.username, credentials.password)
    if not auth_user[0]:
        raise HTTPException(status_code=auth_user[1], detail=auth_user[2])

    if auth_user[1].role != "seller":
        raise HTTPException(
            status_code=400, detail="Sorry but you have to be a seller to add a product"
        )

    # check if the product already exists fot the user
    db_product = utils.get_product_for_user(
        db, product_name=product.product_name, seller_id=auth_user[1].id
    )
    if db_product:
        raise HTTPException(
            status_code=400, detail="Product for user already registered"
        )
    return utils.create_user_product(db=db, product=product, seller_id=auth_user[1].id)


@router.get("/product/{product_name}")
def read_product_by_product_name(
    product_name: str, db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Get a product info by name
    :param product_name: product ma,e
    :param db: database session
    :return: product info
    """
    db_product = utils.get_all_products(db, product_name=product_name)
    if db_product is None:
        raise HTTPException(status_code=400, detail="Product not found")
    return db_product


@router.delete("/product/{product_name}")
def remove_product(
    product_name: str,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
):
    """
    Remove a product for the logged user
    :param product_name: the product name
    :param db: database session
    :param credentials: user credentials
    :return: the removed product
    """
    # first check if the credentials are ok
    auth_user = utils.authenticate_user(db, credentials.username, credentials.password)
    if not auth_user[0]:
        raise HTTPException(status_code=auth_user[1], detail=auth_user[2])

    db_product = utils.get_product_for_user(
        db, product_name=product_name, seller_id=auth_user[1].id
    )

    if not db_product:
        raise HTTPException(
            status_code=400,
            detail="Sorry but can't find the product with the specified name for the user",
        )

    utils.remove_product(db, product_name, auth_user[1].id)

    return db_product


@router.put("/product/{product_name}")
def update_product(
    product_name: str,
    new_product_details: ProductCreate,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
):
    """

    :param product_name: the product name
    :param new_product_details: new product details to update
    :param db: database session
    :param credentials: user credentials
    :return: new product info
    """
    # first check if the credentials are ok
    auth_user = utils.authenticate_user(db, credentials.username, credentials.password)
    if not auth_user[0]:
        raise HTTPException(status_code=auth_user[1], detail=auth_user[2])

    db_product = utils.get_product_for_user(db, product_name, auth_user[1].id)

    if not db_product:
        raise HTTPException(
            status_code=400, detail="Product can't be found for the user"
        )

    # check if the new product_name is already taken
    if utils.get_product_for_user(
        db, new_product_details.product_name, auth_user[1].id
    ):
        raise HTTPException(
            status_code=400, detail="Sorry but there's already a product with this name"
        )

    return utils.update_product(db, product_name, auth_user[1].id, new_product_details)


@router.get("/buy")
def buy_product(
    product_id: int,
    amount: int,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
):
    """

    :param product_id: the product id the user want to buy
    :param amount: amount of product
    :param db: database session
    :param credentials: user credentials
    :return: total_spent, product_name, change
    """
    # first check if the credentials/role are ok
    auth_user = utils.authenticate_user(
        db, credentials.username, credentials.password, buyer_requester=True
    )
    if not auth_user[0]:
        if auth_user[1] == 401:
            raise HTTPException(status_code=auth_user[1], detail=auth_user[2])
        if auth_user[1] == 400:
            raise HTTPException(
                status_code=auth_user[1],
                detail=auth_user[2],
            )

    # get product info
    product_info = utils.get_product_by_id(db, product_id)

    # check if user have enough deposit to buy the requested amount
    if (user_deposit := auth_user[1].deposit) < (amount * product_info.cost):
        if user_deposit == 0:
            raise HTTPException(
                status_code=400, detail="Your balance is 0. Please refill your account"
            )

        # tell the user what amount he can buy
        max_items_can_buy = user_deposit // product_info.cost
        if max_items_can_buy > 0:
            raise HTTPException(
                status_code=400, detail=f"You can buy: {max_items_can_buy} pcs!"
            )

        # the user is not able to buy any item
        raise HTTPException(
            status_code=400,
            detail=f"You can buy no pcs. Try deposit or chose another product!",
        )

    # check if the amount of product is available for sale
    if (product_amount := product_info.amount_available) < amount:
        if product_amount == 0:
            raise HTTPException(
                status_code=400,
                detail="No product amount available. Please try another product",
            )
        raise HTTPException(
            status_code=400,
            detail=f"Only {product_info.amount_available} pcs available",
        )

    new_product_amount_available = product_info.amount_available - amount
    user_change = auth_user[1].deposit - (amount * product_info.cost)

    utils.update_user_deposit(db, credentials.username, user_change)
    utils.update_product_amount_available_by_id(
        db, product_id, new_product_amount_available
    )

    return {
        "total_spent": amount,
        "product_name": product_info.product_name,
        "change": user_change,
    }
