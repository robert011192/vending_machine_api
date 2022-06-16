from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, validator

from core.serializers import CamelModel


class Roles(Enum):
    buyer = "buyer"
    seller = "seller"
    admin = "admin"


class UserBase(CamelModel):
    password: str
    deposit: int = 0
    role: Roles

    class Config:
        use_enum_values = True


class User(UserBase):
    username: str

    class Config:
        orm_mode = True


class UserAuth(BaseModel):
    username: str = Field(..., description="user name")
    password: str = Field(..., min_length=5, max_length=20, description="user password")


class UserInfo(BaseModel):
    id: UUID
    username: str


COIN_VALUE_LIST = [5, 10, 20, 50, 100]


class CoinValue(BaseModel):
    coin_value: int

    @validator("coin_value", pre=True)
    def is_in_list(cls, v) -> int:
        if v not in COIN_VALUE_LIST:
            raise ValueError(
                f"You should deposit a value from this list: {COIN_VALUE_LIST}"
            )

        return v
