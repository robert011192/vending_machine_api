from pydantic import validator

from core.serializers import CamelModel


class ProductBase(CamelModel):
    amount_available: int
    cost: int
    product_name: str

    @validator("cost")
    def is_multiple_of_5(cls, v) -> bool:
        if not v % 5 == 0:
            raise ValueError("Cost must be multiple of 5")

        return v


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    seller_id: str

    class Config:
        orm_mode = True
