from fastapi import FastAPI
from api.separate import router

app = FastAPI()
app.include_router(router)