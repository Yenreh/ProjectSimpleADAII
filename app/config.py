import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secreto")
    OUTPUT_PATH = os.getenv("OUTPUT_PATH", "outputs")
