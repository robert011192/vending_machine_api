from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    deposit = Column(Integer, default=0)
    role = Column(String)

    product = relationship("Product", back_populates="seller")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    amount_available = Column(Integer)
    cost = Column(Integer)
    seller_id = Column(Integer, ForeignKey("user.id"))

    seller = relationship("User", back_populates="product")
