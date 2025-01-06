import os
from fastapi import FastAPI
from src.env import config

MODE = config("MODE", default="dev")

app = FastAPI()


@app.get('/', description="home page")
def home_page():
    return {"message": "hello world"}