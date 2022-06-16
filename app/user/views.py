from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from sqlalchemy.orm import Session

from core import utils
from core.database import SessionLocal
from user.serializers import UserBase, CoinValue, User


router = APIRouter()
security = HTTPBasic()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/user", response_model=User)
def create_user(user: User, db: Session = Depends(get_db)):
    """
    Create a user
    :param user: user model info
    :param db: database session
    :return: created user info
    """
    db_user = utils.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return utils.create_user(db=db, user=user)


@router.get("/user/{username}", response_model=User)
def read_user(
    username: str,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
):
    """
    Get a user detail
    :param credentials:
    :param username: user name
    :param db: database session
    :return: user info
    """
    # first check if the credentials are ok
    auth_user = utils.authenticate_user(db, credentials.username, credentials.password)
    if not auth_user[0]:
        raise HTTPException(status_code=auth_user[1], detail=auth_user[2])

    # get username user details
    db_user = utils.get_user(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return db_user


@router.delete("/user/{username}")
def remove_user(
    username: str,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
):
    """
    Here i didn't know who can remove users so i've created another role called `admin`, which is kinda superuser
    :param username: username to remove
    :param db: db Session
    :param credentials: basic auth credentials
    :return: removed user details
    """
    # first check if the credentials are ok and if it's admin
    auth_user = utils.authenticate_user(
        db, credentials.username, credentials.password, admin_requester=True
    )
    if not auth_user[0]:
        if (auth_status_code := auth_user[1]) == 401:
            raise HTTPException(status_code=auth_status_code, detail=auth_user[2])
        raise HTTPException(status_code=auth_user[1], detail=auth_user[2])

    # get user details
    db_user = utils.get_user(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found.")

    utils.remove_user(db, username)
    return db_user


@router.put("/user/{username}")
def update_user(
    username: str,
    new_user_details: UserBase,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
):
    """
    Update users info
    :param username: username to update info
    :param new_user_details: new user details to add
    :param db: database Session
    :param credentials: basic auth credentials
    :return:
    """
    # first check if the credentials are ok
    if not utils.authenticate_user(db, credentials.username, credentials.password):
        raise HTTPException(
            status_code=401, detail="Wrong credentials. Please try again"
        )

    # check for the user
    db_user = utils.get_user(db, username=username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username can't be found")

    if db_user.username != credentials.username:
        raise HTTPException(
            status_code=401, detail="Sorry but you can't update someone else info"
        )

    return utils.update_user(db, username, new_user_details)


@router.put("/deposit")
def deposit_coin(
    coin_value: CoinValue,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
):
    """

    :param coin_value: how many coins to deposit
    :param db: database session
    :param credentials: user credentials
    :return: new details for the user
    """
    # first check if the credentials are ok
    user_auth = utils.authenticate_user(db, credentials.username, credentials.password)
    if not user_auth[0]:
        raise HTTPException(
            status_code=401, detail="Wrong credentials. Please try again"
        )

    if user_auth[1].role != "buyer":
        raise HTTPException(
            status_code=401, detail="You have to be a buyer to be able to deposit"
        )
    new_deposit_value = coin_value.coin_value + user_auth[1].deposit
    return utils.update_user_deposit(db, user_auth[1].username, new_deposit_value)


@router.put("/reset")
def reset_buyer_deposit_to_zero(
    username: str,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
):
    """
    Reset buyer deposit to zero
    :param username: username
    :param db: db session
    :param credentials: credentials
    :return: user info
    """
    # first check if the credentials are ok
    user_auth = utils.authenticate_user(db, credentials.username, credentials.password)
    if not user_auth[0]:
        raise HTTPException(
            status_code=401, detail="Wrong credentials. Please try again"
        )

    if user_auth[1].username != username:
        raise HTTPException(
            status_code=400, detail="Sorry but you can't reset someone else deposit"
        )

    if user_auth[1].role != "buyer":
        raise HTTPException(status_code=400, detail="Sorry but you have to be a buyer")

    return utils.update_user_deposit(db, username, 0)
