from fastapi import FastAPI
from finance.api import router

app = FastAPI()

app.include_router(router,prefix="/transactions",tags=["Transactions"])