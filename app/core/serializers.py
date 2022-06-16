from humps.camel import case
from pydantic import BaseModel


class CamelModel(BaseModel):
    class Config:
        alias_generator = case
        allow_population_by_field_name = True
