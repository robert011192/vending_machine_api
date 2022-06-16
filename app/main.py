from fastapi import FastAPI
from product.views import router as product_api
from user.views import router as user_api

app = FastAPI(
    title="Vending machine",
    description="Vending machine APIs",
    version="0.0.1",
)

###
# Register routers
###
app.include_router(product_api, tags=["Product"])
app.include_router(user_api, tags=["User"])
